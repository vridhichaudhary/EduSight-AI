import os
import django
import sys
import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
import xgboost as xgb

# Setup Django environment
sys.path.append('/Users/pranshu./Documents/EduSight AI/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.ml_pipeline import DataPreprocessor
from apps.students.models import Student

# Get the first student (Demo Student)
student = Student.objects.first()
if not student:
    print("No students found in DB.")
    sys.exit(1)

# Preprocess data
preprocessor = DataPreprocessor(student.id)
try:
    X_train, X_test, y_train, y_test, feature_cols = preprocessor.prepare_for_training()
    X, y, _ = preprocessor.get_feature_matrix()
    
    # Scale features
    X_scaled = preprocessor.scaler.fit_transform(X)
except Exception as e:
    print(f"Error preparing data: {e}")
    sys.exit(1)

# Initialize XGBoost model
model = xgb.XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0,
)

# If we don't have enough data for 5 folds, adjust cv
cv_folds = min(5, len(X))
if cv_folds < 2:
    print("Not enough data to run cross validation.")
    sys.exit(1)

# Run cross validation
scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring='r2')
print(f"CV Folds: {cv_folds}")
print(f"CV R2 Score: {np.mean(scores):.4f} ± {np.std(scores):.4f}")
print(f"Accuracy: {np.mean(scores)*100:.1f}%")
