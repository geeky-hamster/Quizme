from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # email
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin or user
    
    # Relationships
    scores = db.relationship('Score', backref='user', lazy=True)

    def __init__(self, username, password, full_name, qualification, dob, role='user'):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.full_name = full_name
        self.qualification = qualification
        self.dob = dob
        self.role = role

    def __repr__(self):
        return f'User {self.username}'

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'Subject {self.name}'

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'Chapter {self.name}'

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, active, expired
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'Quiz {self.title} for Chapter {self.chapter_id}'
    
    @property
    def is_active(self):
        now = datetime.utcnow()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date)
    
    @property
    def is_expired(self):
        now = datetime.utcnow()
        return now > self.end_date
    
    @property
    def is_upcoming(self):
        now = datetime.utcnow()
        return now < self.start_date

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4

    def __repr__(self):
        return f'Question {self.id} for Quiz {self.quiz_id}'

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Score {self.total_scored}/{self.total_questions} for Quiz {self.quiz_id}'