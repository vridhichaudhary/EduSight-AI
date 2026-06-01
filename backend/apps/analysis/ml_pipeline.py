"""
EduSight AI — Machine Learning Pipeline

Components:
    DataPreprocessor    → Load, clean, feature engineer marks data
    PerformancePredictor → Train and predict with multiple ML models
    ModelEvaluator      → Compare models, select best
    PredictionGenerator → Generate and save predictions to DB

Flow:
    Marks (DB) → DataPreprocessor → PerformancePredictor
    → PredictionGenerator → Prediction (DB)
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from pathlib import Path

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

logger = logging.getLogger('apps.analysis')

# Path where trained models are saved
ML_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / 'ml_models'
ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# DATA PREPROCESSOR
# ─────────────────────────────────────────────
class DataPreprocessor:
    """
    Loads student marks from database and prepares
    feature matrix for ML model training/prediction.

    Features engineered:
        - rolling_avg_3      : Average of last 3 exams
        - rolling_avg_5      : Average of last 5 exams
        - improvement_rate   : Slope of recent trend
        - subject_avg        : Student's avg in this subject
        - overall_avg        : Student's overall avg
        - days_since_last    : Days since previous exam
        - exam_type_encoded  : Numerical encoding of exam type
        - subject_encoded    : Numerical encoding of subject
        - exam_count         : Total exams taken so far
        - grade_level        : Student's grade level
    """

    EXAM_TYPE_MAP = {
        'quiz':       1,
        'assignment': 2,
        'midterm':    3,
        'practical':  4,
        'project':    4,
        'final':      5,
    }

    def __init__(self, student_id: int):
        self.student_id = student_id
        self.df         = None
        self.features   = None
        self.target     = None
        self.scaler     = StandardScaler()
        self.subject_encoder = LabelEncoder()

    def load_data(self) -> pd.DataFrame:
        """
        Load student marks from PostgreSQL via Django ORM.
        Returns raw DataFrame.
        """
        # Import here to avoid circular imports
        from apps.students.models import Marks, Student

        try:
            student = Student.objects.get(pk=self.student_id)
        except Student.DoesNotExist:
            raise ValueError(f"Student {self.student_id} not found")

        marks_qs = Marks.objects.filter(
            student=student
        ).select_related('subject').order_by('exam_date')

        if not marks_qs.exists():
            raise ValueError(
                f"No marks found for student {self.student_id}"
            )

        # Convert queryset to DataFrame
        records = []
        for m in marks_qs:
            records.append({
                'student_id':     self.student_id,
                'grade_level':    student.grade_level,
                'subject':        m.subject.name,
                'subject_id':     m.subject.id,
                'marks_obtained': float(m.marks_obtained),
                'max_marks':      float(m.max_marks),
                'percentage':     float(m.percentage),
                'exam_type':      m.exam_type,
                'exam_date':      pd.to_datetime(m.exam_date),
                'topic':          m.topic or '',
            })

        self.df = pd.DataFrame(records)
        logger.info(
            f"Loaded {len(self.df)} marks for student {self.student_id}"
        )
        return self.df

    def clean_data(self) -> pd.DataFrame:
        """
        Clean loaded DataFrame.
        Handle missing values, outliers, duplicates.
        """
        if self.df is None:
            self.load_data()

        df = self.df.copy()

        # Drop rows with missing critical values
        df = df.dropna(subset=['percentage', 'subject', 'exam_date'])

        # Clip percentages to valid range
        df['percentage'] = df['percentage'].clip(0, 100)

        # Sort by date
        df = df.sort_values('exam_date').reset_index(drop=True)

        # Remove extreme outliers using IQR
        Q1 = df['percentage'].quantile(0.25)
        Q3 = df['percentage'].quantile(0.75)
        IQR = Q3 - Q1
        lower = max(0,   Q1 - 3 * IQR)
        upper = min(100, Q3 + 3 * IQR)
        df = df[
            (df['percentage'] >= lower) &
            (df['percentage'] <= upper)
        ]

        self.df = df
        logger.info(f"Cleaned data: {len(self.df)} rows remaining")
        return self.df

    def engineer_features(self) -> pd.DataFrame:
        """
        Create features from cleaned marks data.
        Returns DataFrame with feature columns.
        """
        if self.df is None or len(self.df) == 0:
            raise ValueError("No data to engineer features from")

        df = self.df.copy()

        # ── Encode categorical variables ──
        df['exam_type_encoded'] = df['exam_type'].map(
            self.EXAM_TYPE_MAP
        ).fillna(2)

        df['subject_encoded'] = self.subject_encoder.fit_transform(
            df['subject']
        )

        # ── Rolling averages (overall) ──
        df['rolling_avg_3'] = df['percentage'].rolling(
            window=3, min_periods=1
        ).mean()

        df['rolling_avg_5'] = df['percentage'].rolling(
            window=5, min_periods=1
        ).mean()

        # ── Per-subject rolling average ──
        df['subject_rolling_3'] = df.groupby('subject')['percentage'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )

        # ── Improvement rate (slope of recent 5 exams) ──
        def calc_improvement(series):
            arr = series.values
            if len(arr) < 2:
                return 0.0
            x = np.arange(len(arr))
            try:
                slope = np.polyfit(x, arr, 1)[0]
                return float(slope)
            except Exception:
                return 0.0

        df['improvement_rate'] = df['percentage'].rolling(
            window=5, min_periods=2
        ).apply(calc_improvement, raw=False)
        df['improvement_rate'] = df['improvement_rate'].fillna(0)

        # ── Subject average ──
        subject_avg = df.groupby('subject')['percentage'].transform('mean')
        df['subject_avg'] = subject_avg

        # ── Overall average up to this point ──
        df['overall_avg'] = df['percentage'].expanding().mean()

        # ── Gap from overall average ──
        df['gap_from_avg'] = df['percentage'] - df['overall_avg']

        # ── Days since last exam ──
        df['days_since_last'] = df['exam_date'].diff().dt.days.fillna(0)
        df['days_since_last'] = df['days_since_last'].clip(0, 180)

        # ── Exam count so far ──
        df['exam_count'] = range(1, len(df) + 1)

        # ── Month and season encoding ──
        df['exam_month'] = df['exam_date'].dt.month
        df['exam_quarter'] = df['exam_date'].dt.quarter

        # ── Lag features (previous score) ──
        df['prev_score']      = df['percentage'].shift(1).fillna(
            df['percentage'].mean()
        )
        df['prev_subject_score'] = df.groupby('subject')['percentage'].shift(
            1
        ).fillna(df['percentage'].mean())

        self.df = df
        logger.info(f"Engineered {len(df.columns)} features")
        return self.df

    def get_feature_matrix(self):
        """
        Return X (features) and y (target) arrays
        for model training.
        """
        if self.df is None:
            raise ValueError("Call engineer_features() first")

        feature_cols = [
            'rolling_avg_3',
            'rolling_avg_5',
            'subject_rolling_3',
            'improvement_rate',
            'subject_avg',
            'overall_avg',
            'gap_from_avg',
            'days_since_last',
            'exam_type_encoded',
            'subject_encoded',
            'exam_count',
            'exam_month',
            'exam_quarter',
            'prev_score',
            'prev_subject_score',
            'grade_level',
        ]

        available_cols = [
            c for c in feature_cols if c in self.df.columns
        ]

        X = self.df[available_cols].fillna(0).values
        y = self.df['percentage'].values

        return X, y, available_cols

    def prepare_for_training(self, test_size=0.2):
        """
        Full pipeline: load → clean → engineer → split.
        Returns train/test splits.
        """
        self.load_data()
        self.clean_data()
        self.engineer_features()
        X, y, feature_cols = self.get_feature_matrix()

        if len(X) < 4:
            raise ValueError(
                f"Not enough data for training. "
                f"Have {len(X)} samples, need at least 4."
            )

        # Split (if enough data, else use all for training)
        if len(X) >= 8:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
        else:
            # Use all data for training (tiny dataset)
            X_train, X_test = X, X
            y_train, y_test = y, y

        logger.info(
            f"Data split: {len(X_train)} train, {len(X_test)} test"
        )
        return X_train, X_test, y_train, y_test, feature_cols

# ─────────────────────────────────────────────
# PERFORMANCE PREDICTOR
# ─────────────────────────────────────────────
class PerformancePredictor:
    """
    Trains multiple regression models on student marks data.
    Selects best model by cross-validated MAE.
    Saves and loads models to/from disk.

    Models trained:
        - LinearRegression (baseline)
        - Ridge (regularized linear)
        - RandomForestRegressor (main ensemble)
        - GradientBoostingRegressor (boosting)
        - XGBRegressor (best, if available)
    """

    def __init__(self, student_id: int):
        self.student_id  = student_id
        self.best_model  = None
        self.best_name   = None
        self.best_score  = None
        self.all_scores  = {}
        self.scaler      = StandardScaler()
        self.is_trained  = False

    def _get_models(self):
        """Return dict of model name → model instance."""
        models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'RandomForest': RandomForestRegressor(
                n_estimators=100,
                max_depth=6,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42,
            ),
        }

        if XGBOOST_AVAILABLE:
            models['XGBoost'] = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
            )

        return models

    def train(self, X_train, y_train):
        """
        Train all models.
        Select best by cross-validated MAE.
        """
        logger.info(
            f"Training models for student {self.student_id} "
            f"on {len(X_train)} samples"
        )

        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        models = self._get_models()
        best_mae  = float('inf')
        best_name = None
        best_model = None

        for name, model in models.items():
            try:
                # Cross-validate (use min 3 folds)
                cv_folds = min(3, len(X_train))
                if cv_folds < 2:
                    model.fit(X_scaled, y_train)
                    preds = model.predict(X_scaled)
                    mae = mean_absolute_error(y_train, preds)
                else:
                    scores = cross_val_score(
                        model,
                        X_scaled,
                        y_train,
                        cv=cv_folds,
                        scoring='neg_mean_absolute_error',
                        n_jobs=-1,
                    )
                    mae = -scores.mean()
                    # Retrain on full training set
                    model.fit(X_scaled, y_train)

                self.all_scores[name] = round(mae, 4)
                logger.info(f"  {name}: MAE = {mae:.4f}")

                if mae < best_mae:
                    best_mae   = mae
                    best_name  = name
                    best_model = model

            except Exception as e:
                logger.warning(f"  {name} failed: {str(e)}")

        self.best_model  = best_model
        self.best_name   = best_name
        self.best_score  = best_mae
        self.is_trained  = True

        logger.info(
            f"Best model: {best_name} (MAE={best_mae:.4f})"
        )
        return self

    def evaluate(self, X_test, y_test) -> dict:
        """Evaluate best model on test set."""
        if not self.is_trained:
            raise ValueError("Train the model first")

        X_scaled = self.scaler.transform(X_test)
        y_pred = self.best_model.predict(X_scaled)

        # Clip predictions to valid range
        y_pred = np.clip(y_pred, 0, 100)

        metrics = {
            'mae':         round(mean_absolute_error(y_test, y_pred), 4),
            'rmse':        round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
            'r2':          round(r2_score(y_test, y_pred), 4),
            'model_name':  self.best_name,
            'all_scores':  self.all_scores,
        }

        logger.info(f"Evaluation: {metrics}")
        return metrics

    def predict(self, X: np.ndarray) -> tuple:
        """
        Predict percentage score for given features.
        Returns (prediction, lower_bound, upper_bound, confidence).
        """
        if not self.is_trained:
            raise ValueError("Train the model first")

        X_scaled = self.scaler.transform(X.reshape(1, -1))
        prediction = float(self.best_model.predict(X_scaled)[0])
        prediction = np.clip(prediction, 0, 100)

        # Estimate confidence interval using model error
        mae = self.best_score or 5.0
        confidence = max(0.5, min(0.99, 1.0 - (mae / 50)))
        lower = max(0,   prediction - (mae * 1.5))
        upper = min(100, prediction + (mae * 1.5))

        return (
            round(prediction, 2),
            round(lower, 2),
            round(upper, 2),
            round(confidence, 4),
        )

    def save_model(self):
        """Save trained model and scaler to disk."""
        if not self.is_trained:
            raise ValueError("Train model before saving")

        model_path  = ML_MODELS_DIR / f"model_student_{self.student_id}.pkl"
        scaler_path = ML_MODELS_DIR / f"scaler_student_{self.student_id}.pkl"
        meta_path   = ML_MODELS_DIR / f"meta_student_{self.student_id}.pkl"

        joblib.dump(self.best_model, model_path)
        joblib.dump(self.scaler,     scaler_path)
        joblib.dump({
            'best_name':  self.best_name,
            'best_score': self.best_score,
            'all_scores': self.all_scores,
        }, meta_path)

        logger.info(f"Model saved: {model_path}")
        return str(model_path)

    def load_model(self):
        """Load trained model from disk."""
        model_path  = ML_MODELS_DIR / f"model_student_{self.student_id}.pkl"
        scaler_path = ML_MODELS_DIR / f"scaler_student_{self.student_id}.pkl"
        meta_path   = ML_MODELS_DIR / f"meta_student_{self.student_id}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"No saved model for student {self.student_id}. "
                f"Train the model first."
            )

        self.best_model = joblib.load(model_path)
        self.scaler     = joblib.load(scaler_path)
        meta            = joblib.load(meta_path)
        self.best_name  = meta['best_name']
        self.best_score = meta['best_score']
        self.all_scores = meta['all_scores']
        self.is_trained = True

        logger.info(f"Model loaded: {self.best_name}")
        return self

    def model_exists(self) -> bool:
        """Check if a trained model exists for this student."""
        path = ML_MODELS_DIR / f"model_student_{self.student_id}.pkl"
        return path.exists()

# ─────────────────────────────────────────────
# PREDICTION GENERATOR
# ─────────────────────────────────────────────
class PredictionGenerator:
    """
    Orchestrates full ML pipeline for a student:
    1. Preprocess data
    2. Train/load model
    3. Generate predictions per subject
    4. Save predictions to database
    """

    def __init__(self, student_id: int):
        self.student_id  = student_id
        self.preprocessor = DataPreprocessor(student_id)
        self.predictor    = PerformancePredictor(student_id)

    def run(self, retrain: bool = False) -> dict:
        """
        Full pipeline execution.
        Returns dict with predictions and metrics.
        """
        from apps.students.models import Student, Subject, Prediction

        logger.info(
            f"Running prediction pipeline for student {self.student_id}"
        )

        # ── Step 1: Prepare data ──
        try:
            X_train, X_test, y_train, y_test, feature_cols = (
                self.preprocessor.prepare_for_training()
            )
        except ValueError as e:
            logger.error(f"Data prep failed: {str(e)}")
            return {'success': False, 'error': str(e)}

        # ── Step 2: Train or load model ──
        if retrain or not self.predictor.model_exists():
            self.predictor.train(X_train, y_train)
            self.predictor.save_model()
            metrics = self.predictor.evaluate(X_test, y_test)
        else:
            try:
                self.predictor.load_model()
                metrics = {'model_name': self.predictor.best_name}
            except FileNotFoundError:
                self.predictor.train(X_train, y_train)
                self.predictor.save_model()
                metrics = self.predictor.evaluate(X_test, y_test)

        # ── Step 3: Generate per-subject predictions ──
        df = self.preprocessor.df
        predictions_created = []

        subjects = df['subject'].unique()

        for subject_name in subjects:
            try:
                subject_df = df[df['subject'] == subject_name].copy()

                if len(subject_df) == 0:
                    continue

                # Use latest row as features for prediction
                latest = subject_df.iloc[-1]
                X_pred = self.preprocessor.df[
                    self.preprocessor.df['subject'] == subject_name
                ].tail(1)

                _, _, available_cols = (
                    self.preprocessor.get_feature_matrix()
                )
                X_features = X_pred[available_cols].fillna(0).values[0]

                predicted, lower, upper, confidence = (
                    self.predictor.predict(X_features)
                )

                # Get Django objects
                try:
                    student = Student.objects.get(pk=self.student_id)
                    subject = Subject.objects.get(name=subject_name)
                except Exception:
                    continue

                # Save to database (update or create)
                prediction_date = (
                    datetime.now() + timedelta(days=30)
                ).date()

                pred_obj, created = Prediction.objects.update_or_create(
                    student=student,
                    subject=subject,
                    prediction_reason='next_exam',
                    defaults={
                        'predicted_marks':    predicted,
                        'confidence_score':   confidence,
                        'lower_bound':        lower,
                        'upper_bound':        upper,
                        'prediction_for_date': prediction_date,
                        'model_name':          self.predictor.best_name,
                        'model_version':       '1.0',
                        'features_used':       available_cols,
                    }
                )

                predictions_created.append({
                    'subject':          subject_name,
                    'predicted_marks':  predicted,
                    'confidence_score': confidence,
                    'is_new':           created,
                })

                logger.info(
                    f"Prediction saved: {subject_name} → {predicted}%"
                )

            except Exception as e:
                logger.error(
                    f"Prediction failed for {subject_name}: {str(e)}"
                )

        return {
            'success':              True,
            'student_id':           self.student_id,
            'predictions_created':  len(predictions_created),
            'predictions':          predictions_created,
            'model_name':           self.predictor.best_name,
            'metrics':              metrics,
        }
