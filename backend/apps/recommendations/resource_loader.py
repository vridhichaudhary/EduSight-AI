"""
EduSight AI — Educational Resource Database

Contains curated study resources across subjects.
These get embedded into FAISS for semantic search.

Structure per resource:
    id          : unique identifier
    subject     : academic subject
    topic       : specific topic within subject
    title       : resource title
    type        : video | article | practice | book | interactive
    url         : real URL to the resource
    description : detailed description (used for embedding)
    difficulty  : beginner | intermediate | advanced
    grade_range : '6-8' | '9-10' | '11-12' | 'all'
    tags        : list of search terms

Adding resources:
    Extend the RESOURCES list below.
    Run: python manage.py build_vectorstore
    to rebuild the FAISS index.
"""

from typing import List, Dict


RESOURCES: List[Dict] = [

    # ─────────────────────────────────────
    # MATHEMATICS
    # ─────────────────────────────────────
    {
        'id':          'math_001',
        'subject':     'Mathematics',
        'topic':       'Algebra',
        'title':       'Khan Academy: Algebra Fundamentals',
        'type':        'video',
        'url':         'https://www.khanacademy.org/math/algebra',
        'description': (
            'Comprehensive algebra course covering linear equations, '
            'inequalities, functions, and graphing. Perfect for students '
            'struggling with algebra fundamentals. Includes practice '
            'exercises and worked examples with step-by-step solutions.'
        ),
        'difficulty':  'beginner',
        'grade_range': '8-10',
        'tags':        ['algebra', 'equations', 'linear', 'functions',
                        'mathematics', 'variables'],
    },
    {
        'id':          'math_002',
        'subject':     'Mathematics',
        'topic':       'Calculus',
        'title':       'Khan Academy: Differential Calculus',
        'type':        'video',
        'url':         'https://www.khanacademy.org/math/differential-calculus',
        'description': (
            'Complete differential calculus course with limits, '
            'derivatives, and their applications. Covers chain rule, '
            'product rule, and quotient rule with detailed examples. '
            'Ideal for students preparing for board exams or struggling '
            'with calculus concepts and derivatives.'
        ),
        'difficulty':  'advanced',
        'grade_range': '11-12',
        'tags':        ['calculus', 'derivatives', 'limits', 'differentiation',
                        'mathematics', 'advanced'],
    },
    {
        'id':          'math_003',
        'subject':     'Mathematics',
        'topic':       'Geometry',
        'title':       'Khan Academy: Geometry',
        'type':        'video',
        'url':         'https://www.khanacademy.org/math/geometry',
        'description': (
            'Full geometry course covering triangles, circles, '
            'polygons, coordinate geometry, and proofs. Interactive '
            'exercises help students visualize geometric concepts. '
            'Excellent for students who struggle with shapes, angles, '
            'and spatial reasoning problems.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-11',
        'tags':        ['geometry', 'triangles', 'circles', 'polygons',
                        'angles', 'proofs', 'coordinate'],
    },
    {
        'id':          'math_004',
        'subject':     'Mathematics',
        'topic':       'Statistics',
        'title':       'Khan Academy: Statistics and Probability',
        'type':        'video',
        'url':         'https://www.khanacademy.org/math/statistics-probability',
        'description': (
            'Statistics and probability course including mean, median, '
            'mode, standard deviation, normal distributions, and '
            'probability theory. Includes real-world data analysis '
            'exercises. Great for students who find statistics '
            'confusing or need help with data interpretation.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['statistics', 'probability', 'mean', 'median',
                        'standard deviation', 'data', 'graphs'],
    },
    {
        'id':          'math_005',
        'subject':     'Mathematics',
        'topic':       'Trigonometry',
        'title':       'Khan Academy: Trigonometry',
        'type':        'video',
        'url':         'https://www.khanacademy.org/math/trigonometry',
        'description': (
            'Complete trigonometry course covering sine, cosine, tangent, '
            'trigonometric identities, and their applications. Includes '
            'unit circle, graphs of trig functions, and inverse trig. '
            'Perfect for students struggling with angles, waves, and '
            'trigonometric problem solving.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['trigonometry', 'sine', 'cosine', 'tangent',
                        'angles', 'identities', 'unit circle'],
    },
    {
        'id':          'math_006',
        'subject':     'Mathematics',
        'topic':       'Practice Problems',
        'title':       'NCERT Exemplar Mathematics',
        'type':        'practice',
        'url':         'https://ncert.nic.in/exemplar-problems.php',
        'description': (
            'Official NCERT exemplar problems for Mathematics covering '
            'all chapters. Higher-order thinking problems that go beyond '
            'textbook exercises. Essential for board exam preparation '
            'and students who need challenging practice to improve their '
            'mathematics performance and problem-solving skills.'
        ),
        'difficulty':  'advanced',
        'grade_range': '9-12',
        'tags':        ['ncert', 'practice', 'problems', 'board exam',
                        'mathematics', 'exemplar', 'exercises'],
    },
    {
        'id':          'math_007',
        'subject':     'Mathematics',
        'topic':       'Number Theory',
        'title':       'Art of Problem Solving: Number Theory',
        'type':        'article',
        'url':         'https://artofproblemsolving.com/wiki/index.php/Number_theory',
        'description': (
            'In-depth number theory resources covering divisibility, '
            'prime numbers, GCD, LCM, and modular arithmetic. Excellent '
            'for olympiad preparation and students who want to deepen '
            'their understanding of mathematical proofs and integer '
            'properties beyond standard curriculum.'
        ),
        'difficulty':  'advanced',
        'grade_range': '11-12',
        'tags':        ['number theory', 'primes', 'divisibility',
                        'modular', 'olympiad', 'competition'],
    },

    # ─────────────────────────────────────
    # SCIENCE / PHYSICS
    # ─────────────────────────────────────
    {
        'id':          'sci_001',
        'subject':     'Science',
        'topic':       'Physics: Mechanics',
        'title':       'Khan Academy: Physics — Forces and Motion',
        'type':        'video',
        'url':         'https://www.khanacademy.org/science/physics',
        'description': (
            'Physics course covering Newton laws of motion, forces, '
            'momentum, energy, and work. Includes problem-solving '
            'techniques for mechanics questions. Ideal for students '
            'struggling with motion, velocity, acceleration, and '
            'applying physics formulas to real-world scenarios.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-11',
        'tags':        ['physics', 'mechanics', 'forces', 'motion',
                        'newton', 'velocity', 'acceleration', 'energy'],
    },
    {
        'id':          'sci_002',
        'subject':     'Science',
        'topic':       'Chemistry: Reactions',
        'title':       'Khan Academy: Chemistry',
        'type':        'video',
        'url':         'https://www.khanacademy.org/science/chemistry',
        'description': (
            'Complete chemistry course covering atomic structure, '
            'chemical bonding, reactions, stoichiometry, acids and bases, '
            'and thermodynamics. Step-by-step problem solving for '
            'balancing equations. Perfect for students who struggle '
            'with chemical reactions, formulas, and quantitative chemistry.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['chemistry', 'reactions', 'stoichiometry',
                        'bonding', 'acids', 'periodic table', 'equations'],
    },
    {
        'id':          'sci_003',
        'subject':     'Science',
        'topic':       'Biology: Cell Biology',
        'title':       'Khan Academy: Biology',
        'type':        'video',
        'url':         'https://www.khanacademy.org/science/biology',
        'description': (
            'Comprehensive biology course covering cell biology, '
            'genetics, evolution, ecology, and human physiology. '
            'Detailed diagrams and animations explain complex '
            'biological processes. Essential for students who find '
            'biology concepts abstract or struggle with memorizing '
            'biological terminology and processes.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['biology', 'cells', 'genetics', 'DNA', 'evolution',
                        'ecology', 'physiology', 'organisms'],
    },
    {
        'id':          'sci_004',
        'subject':     'Science',
        'topic':       'Physics: Electricity',
        'title':       'Khan Academy: Electrical Engineering Basics',
        'type':        'video',
        'url':         'https://www.khanacademy.org/science/electrical-engineering',
        'description': (
            'Electricity and magnetism fundamentals including circuits, '
            'Ohm law, current, voltage, and electromagnetic induction. '
            'Visual simulations make abstract concepts concrete. '
            'Great for students struggling with electricity concepts, '
            'circuit diagrams, and electromagnetic theory in physics.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['electricity', 'circuits', 'current', 'voltage',
                        'magnetism', 'ohm', 'resistance', 'physics'],
    },
    {
        'id':          'sci_005',
        'subject':     'Science',
        'topic':       'Practice and Revision',
        'title':       'NCERT Science Exemplar Problems',
        'type':        'practice',
        'url':         'https://ncert.nic.in/exemplar-problems.php',
        'description': (
            'Official NCERT exemplar problems for Science including '
            'Physics, Chemistry, and Biology. Higher-order thinking '
            'questions for board exam preparation. Critical for students '
            'who need structured practice beyond textbook problems '
            'to improve science examination performance.'
        ),
        'difficulty':  'advanced',
        'grade_range': '9-12',
        'tags':        ['ncert', 'science', 'practice', 'board exam',
                        'physics', 'chemistry', 'biology', 'exemplar'],
    },
    {
        'id':          'sci_006',
        'subject':     'Science',
        'topic':       'Environmental Science',
        'title':       'Crash Course: Environmental Science',
        'type':        'video',
        'url':         'https://www.youtube.com/playlist?list=PL8dPuuaLjXtNdTKZkV_GiIYXpV9w4WxbX',
        'description': (
            'Engaging environmental science series covering ecosystems, '
            'climate change, biodiversity, sustainability, and human '
            'impact on the environment. Animated, fast-paced videos '
            'make complex environmental concepts accessible and memorable '
            'for students who find environmental science dry or difficult.'
        ),
        'difficulty':  'beginner',
        'grade_range': '8-12',
        'tags':        ['environment', 'ecology', 'climate', 'ecosystem',
                        'sustainability', 'biodiversity', 'science'],
    },

    # ─────────────────────────────────────
    # ENGLISH
    # ─────────────────────────────────────
    {
        'id':          'eng_001',
        'subject':     'English',
        'topic':       'Grammar',
        'title':       'Grammarly: Grammar Handbook',
        'type':        'article',
        'url':         'https://www.grammarly.com/blog/category/handbook',
        'description': (
            'Comprehensive grammar guide covering parts of speech, '
            'sentence structure, punctuation, tense, and common errors. '
            'Clear examples with explanations. Essential for students '
            'struggling with English grammar, writing essays, or making '
            'frequent grammatical mistakes in examinations.'
        ),
        'difficulty':  'beginner',
        'grade_range': 'all',
        'tags':        ['grammar', 'writing', 'punctuation', 'tense',
                        'sentences', 'english', 'essays', 'language'],
    },
    {
        'id':          'eng_002',
        'subject':     'English',
        'topic':       'Essay Writing',
        'title':       'Purdue OWL: Academic Writing Guide',
        'type':        'article',
        'url':         'https://owl.purdue.edu/owl/general_writing',
        'description': (
            'Academic writing resource covering essay structure, '
            'thesis statements, argumentation, citations, and research '
            'writing. Step-by-step guides for different essay types. '
            'Perfect for students who struggle with essay structure, '
            'academic language, or organizing their thoughts clearly '
            'in written examinations.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['essay', 'writing', 'academic', 'thesis',
                        'argument', 'structure', 'english', 'literature'],
    },
    {
        'id':          'eng_003',
        'subject':     'English',
        'topic':       'Reading Comprehension',
        'title':       'Khan Academy: Reading and Language Arts',
        'type':        'practice',
        'url':         'https://www.khanacademy.org/ela',
        'description': (
            'Reading comprehension practice including inference, '
            'main idea identification, vocabulary in context, and '
            'literary analysis. Passages from various genres with '
            'guided questions. Ideal for students scoring low in '
            'comprehension sections or struggling with extracting '
            'meaning from complex texts.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '8-12',
        'tags':        ['reading', 'comprehension', 'vocabulary',
                        'inference', 'literary analysis', 'english'],
    },
    {
        'id':          'eng_004',
        'subject':     'English',
        'topic':       'Literature Analysis',
        'title':       'SparkNotes: Literature Study Guides',
        'type':        'article',
        'url':         'https://www.sparknotes.com',
        'description': (
            'Detailed literature analysis guides covering themes, '
            'characters, plot summaries, symbolism, and critical '
            'interpretations of classic and contemporary works. '
            'Essential for students struggling with literary analysis, '
            'understanding themes in novels and plays, or preparing '
            'for literature examinations.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['literature', 'analysis', 'themes', 'characters',
                        'novels', 'poetry', 'english', 'symbolism'],
    },
    {
        'id':          'eng_005',
        'subject':     'English',
        'topic':       'Vocabulary',
        'title':       'Merriam-Webster Word of the Day',
        'type':        'interactive',
        'url':         'https://www.merriam-webster.com/word-of-the-day',
        'description': (
            'Daily vocabulary building resource with definitions, '
            'etymology, usage examples, and pronunciation. Regular '
            'engagement builds advanced vocabulary for examinations. '
            'Highly effective for students with limited vocabulary '
            'range who struggle with comprehension passages or '
            'need richer language for essay writing.'
        ),
        'difficulty':  'beginner',
        'grade_range': 'all',
        'tags':        ['vocabulary', 'words', 'language', 'english',
                        'definitions', 'usage', 'communication'],
    },

    # ─────────────────────────────────────
    # HISTORY
    # ─────────────────────────────────────
    {
        'id':          'hist_001',
        'subject':     'History',
        'topic':       'World History',
        'title':       'Crash Course: World History',
        'type':        'video',
        'url':         'https://www.youtube.com/playlist?list=PLBDA2E52FB1EF80C9',
        'description': (
            'Engaging world history series from ancient civilizations '
            'to modern times. Covers major events, empires, revolutions, '
            'and their causes and consequences. Animated and fast-paced '
            'format helps students remember key historical events and '
            'understand historical patterns and cause-effect relationships.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['history', 'world history', 'civilizations',
                        'empires', 'revolutions', 'events', 'timeline'],
    },
    {
        'id':          'hist_002',
        'subject':     'History',
        'topic':       'Modern History',
        'title':       'Khan Academy: World History Project',
        'type':        'video',
        'url':         'https://www.khanacademy.org/humanities/whp-origins',
        'description': (
            'Comprehensive world history covering origins of humanity '
            'through modern globalization. Primary source analysis, '
            'timelines, and essay writing practice included. Perfect '
            'for students who struggle with understanding historical '
            'context, chronology, and writing analytical history essays.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['history', 'modern history', 'globalization',
                        'primary sources', 'analysis', 'chronology'],
    },
    {
        'id':          'hist_003',
        'subject':     'History',
        'topic':       'Essay Writing for History',
        'title':       'BBC History: Essay Writing Techniques',
        'type':        'article',
        'url':         'https://www.bbc.co.uk/bitesize/examskills',
        'description': (
            'History-specific essay writing guide covering argument '
            'construction, use of evidence, evaluating sources, and '
            'structuring analytical responses. Includes model answers '
            'and marking criteria. Essential for students losing marks '
            'in history essays due to poor structure or weak arguments.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['history', 'essay', 'writing', 'evidence',
                        'sources', 'analysis', 'exam technique'],
    },

    # ─────────────────────────────────────
    # GEOGRAPHY
    # ─────────────────────────────────────
    {
        'id':          'geo_001',
        'subject':     'Geography',
        'topic':       'Physical Geography',
        'title':       'Khan Academy: Geography',
        'type':        'video',
        'url':         'https://www.khanacademy.org/humanities/ap-human-geography',
        'description': (
            'Human and physical geography covering climate systems, '
            'landforms, population patterns, urbanization, and economic '
            'geography. Map-based learning helps students visualize '
            'geographic concepts. Great for students who find geography '
            'theoretical and need concrete visual explanations.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '9-12',
        'tags':        ['geography', 'physical geography', 'climate',
                        'landforms', 'population', 'maps', 'environment'],
    },
    {
        'id':          'geo_002',
        'subject':     'Geography',
        'topic':       'Map Skills',
        'title':       'National Geographic: Map Skills',
        'type':        'interactive',
        'url':         'https://education.nationalgeographic.org/resource/map-skills',
        'description': (
            'Interactive map skills resources including topographic maps, '
            'climate maps, political maps, and satellite imagery analysis. '
            'Essential for students struggling with map reading, scale, '
            'direction, and interpreting geographic data. Hands-on '
            'exercises build practical geography skills for exams.'
        ),
        'difficulty':  'beginner',
        'grade_range': '8-12',
        'tags':        ['geography', 'maps', 'topographic', 'satellite',
                        'scale', 'direction', 'spatial'],
    },

    # ─────────────────────────────────────
    # COMPUTER SCIENCE
    # ─────────────────────────────────────
    {
        'id':          'cs_001',
        'subject':     'Computer Science',
        'topic':       'Programming Fundamentals',
        'title':       'Khan Academy: Computer Programming',
        'type':        'interactive',
        'url':         'https://www.khanacademy.org/computing/computer-programming',
        'description': (
            'Interactive programming course covering variables, loops, '
            'functions, arrays, and object-oriented programming. '
            'Hands-on coding exercises in the browser. Perfect for '
            'students struggling with programming logic, debugging, '
            'or understanding how algorithms and code work together.'
        ),
        'difficulty':  'beginner',
        'grade_range': '9-12',
        'tags':        ['programming', 'coding', 'python', 'algorithms',
                        'computer science', 'functions', 'loops'],
    },
    {
        'id':          'cs_002',
        'subject':     'Computer Science',
        'topic':       'Data Structures',
        'title':       'Visualgo: Data Structure Visualizations',
        'type':        'interactive',
        'url':         'https://visualgo.net/en',
        'description': (
            'Visual interactive learning platform for data structures '
            'and algorithms. Animations show how arrays, linked lists, '
            'trees, graphs, and sorting algorithms work step by step. '
            'Ideal for students who struggle with abstract data structure '
            'concepts and need visual representation to understand them.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '10-12',
        'tags':        ['data structures', 'algorithms', 'sorting',
                        'trees', 'graphs', 'computer science', 'visual'],
    },
    {
        'id':          'cs_003',
        'subject':     'Computer Science',
        'topic':       'Theory and Concepts',
        'title':       'CS50: Introduction to Computer Science',
        'type':        'video',
        'url':         'https://cs50.harvard.edu/x',
        'description': (
            'Harvard free introductory computer science course covering '
            'computational thinking, algorithms, data representation, '
            'and software engineering. World-class instruction with '
            'problem sets. Exceptional for students who want deep '
            'understanding of computer science fundamentals beyond '
            'basic programming syntax.'
        ),
        'difficulty':  'intermediate',
        'grade_range': '11-12',
        'tags':        ['computer science', 'algorithms', 'harvard',
                        'programming', 'computational thinking', 'cs50'],
    },

    # ─────────────────────────────────────
    # GENERAL STUDY SKILLS
    # ─────────────────────────────────────
    {
        'id':          'study_001',
        'subject':     'General',
        'topic':       'Study Techniques',
        'title':       'Learning How to Learn: Coursera',
        'type':        'video',
        'url':         'https://www.coursera.org/learn/learning-how-to-learn',
        'description': (
            'Science-based learning techniques including spaced repetition, '
            'active recall, the Pomodoro technique, and memory palaces. '
            'Teaches how the brain learns and retains information. '
            'Beneficial for any student regardless of subject, especially '
            'those who study hard but retain little or feel overwhelmed '
            'by examination preparation.'
        ),
        'difficulty':  'beginner',
        'grade_range': 'all',
        'tags':        ['study skills', 'memory', 'learning', 'revision',
                        'exam preparation', 'productivity', 'focus'],
    },
    {
        'id':          'study_002',
        'subject':     'General',
        'topic':       'Exam Preparation',
        'title':       'BBC Bitesize: Exam Skills',
        'type':        'article',
        'url':         'https://www.bbc.co.uk/bitesize/examskills',
        'description': (
            'Exam strategy guide covering time management, answering '
            'technique, handling exam anxiety, past paper practice, '
            'and revision planning. Practical advice from examiners. '
            'Essential for students whose exam performance does not '
            'reflect their actual knowledge or who struggle under '
            'timed examination conditions.'
        ),
        'difficulty':  'beginner',
        'grade_range': 'all',
        'tags':        ['exam', 'revision', 'study skills', 'time management',
                        'technique', 'preparation', 'anxiety'],
    },
    {
        'id':          'study_003',
        'subject':     'General',
        'topic':       'Note Taking',
        'title':       'Cornell Notes System',
        'type':        'article',
        'url':         'https://lsc.cornell.edu/how-to-study/taking-notes/cornell-note-taking-system',
        'description': (
            'The Cornell Note-Taking System guides students to organize '
            'notes into cues, notes, and summaries. Proven to improve '
            'retention and active recall during revision. Helpful for '
            'students who take disorganized notes, struggle to review '
            'effectively, or have difficulty extracting key information '
            'from lectures and textbooks.'
        ),
        'difficulty':  'beginner',
        'grade_range': 'all',
        'tags':        ['notes', 'studying', 'organization', 'recall',
                        'cornell', 'revision', 'learning technique'],
    },
]


def get_all_resources() -> List[Dict]:
    """Return full resource list."""
    return RESOURCES


def get_resources_by_subject(subject: str) -> List[Dict]:
    """Filter resources by subject name."""
    subject_lower = subject.lower()
    return [
        r for r in RESOURCES
        if r['subject'].lower() == subject_lower
        or subject_lower in r['description'].lower()
        or subject_lower in ' '.join(r['tags'])
    ]


def get_resource_text(resource: Dict) -> str:
    """
    Generate text representation of resource for embedding.
    Combines all fields for rich semantic search.
    """
    return (
        f"Subject: {resource['subject']}. "
        f"Topic: {resource['topic']}. "
        f"Title: {resource['title']}. "
        f"Description: {resource['description']} "
        f"Tags: {', '.join(resource['tags'])}. "
        f"Difficulty: {resource['difficulty']}. "
        f"Grade: {resource['grade_range']}."
    )


def get_subjects_list() -> List[str]:
    """Return list of unique subjects in resource database."""
    return list(set(r['subject'] for r in RESOURCES))
