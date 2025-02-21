from flask import Flask, request, jsonify
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from datetime import datetime, date
import workers, task
from mailer import mail
from io import BytesIO, StringIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask_caching import Cache

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

# MailHog Configuration
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'quizme@example.com'

app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Enable CORS for all routes with proper configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": "http://localhost:8080",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }
     })

mail.init_app(app)
cache = Cache(app)
celery = workers.celery

celery.conf.update(
    broker_url='redis://localhost:6379/1',
    result_backend='redis://localhost:6379/2'
)

celery.Task = workers.ContextTask
app.app_context().push()

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin@quizmaster.com',
            password='admin123',
            full_name='Quiz Master Admin',
            qualification='PhD',
            dob=date(1990, 1, 1),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

with app.app_context(): 
    db.create_all()
    create_admin()

# Auth Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ['username', 'password', 'full_name', 'qualification', 'dob']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400
    
    try:
        # Convert string date to date object
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        
        new_user = User(
            username=data['username'],
            password=data['password'],
            full_name=data['full_name'],
            qualification=data['qualification'],
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "role": user.role
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401

# Admin Routes
@app.route('/subjects', methods=['GET', 'POST'])
@jwt_required()
def manage_subjects():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    if request.method == 'POST':
        data = request.get_json()
        if not data.get('name'):
            return jsonify({"error": "Subject name is required"}), 400
        
        new_subject = Subject(
            name=data['name'],
            description=data.get('description', '')
        )
        try:
            db.session.add(new_subject)
            db.session.commit()
            return jsonify({"message": "Subject created successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # GET method
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description
    } for s in subjects]), 200

@app.route('/subjects/<int:subject_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_subject(subject_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(subject)
            db.session.commit()
            return jsonify({"message": "Subject deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # PUT method
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "Subject name is required"}), 400
    
    try:
        subject.name = data['name']
        subject.description = data.get('description', subject.description)
        db.session.commit()
        return jsonify({"message": "Subject updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 200

# Chapter Routes
@app.route('/subjects/<int:subject_id>/chapters', methods=['GET', 'POST'])
@jwt_required()
def manage_chapters(subject_id):
    if request.method == 'POST':
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        if not data.get('name'):
            return jsonify({"error": "Chapter name is required"}), 400
        
        new_chapter = Chapter(
            subject_id=subject_id,
            name=data['name'],
            description=data.get('description', '')
        )
        try:
            db.session.add(new_chapter)
            db.session.commit()
            return jsonify({"message": "Chapter created successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # GET method
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in chapters]), 200

@app.route('/chapters/<int:chapter_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_chapter(chapter_id):
    current_user = get_jwt_identity()
    
    # GET method
    if request.method == 'GET':
        chapter = Chapter.query.get_or_404(chapter_id)
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id
        }), 200
    
    # For PUT and DELETE methods, check admin authorization
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(chapter)
            db.session.commit()
            return jsonify({"message": "Chapter deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # PUT method
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "Chapter name is required"}), 400
    
    try:
        chapter.name = data['name']
        chapter.description = data.get('description', chapter.description)
        db.session.commit()
        return jsonify({"message": "Chapter updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Quiz Routes
@app.route('/chapters/<int:chapter_id>/quizzes', methods=['GET', 'POST'])
@jwt_required()
def manage_quizzes(chapter_id):
    if request.method == 'POST':
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['title', 'start_date', 'end_date', 'time_duration']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        try:
            # Parse dates from ISO format
            start_date = datetime.fromisoformat(data['start_date'])
            end_date = datetime.fromisoformat(data['end_date'])
            
            if start_date >= end_date:
                return jsonify({"error": "End date must be after start date"}), 400
            
            time_duration = int(data['time_duration'])
            if time_duration <= 0:
                return jsonify({"error": "Time duration must be a positive number of minutes"}), 400
            
            new_quiz = Quiz(
                chapter_id=chapter_id,
                title=data['title'],
                description=data.get('description', ''),
                start_date=start_date,
                end_date=end_date,
                time_duration=time_duration,
                status=data.get('status', 'draft')
            )
            db.session.add(new_quiz)
            db.session.commit()
            return jsonify({"message": "Quiz created successfully", "quiz_id": new_quiz.id}), 201
        except ValueError as e:
            return jsonify({"error": "Invalid date format or time duration. Please check your input."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # GET method
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    now = datetime.utcnow()
    
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'start_date': q.start_date.isoformat(),
        'end_date': q.end_date.isoformat(),
        'time_duration': q.time_duration,
        'status': q.status,
        'is_active': q.is_active,
        'is_expired': q.is_expired,
        'is_upcoming': q.is_upcoming
    } for q in quizzes]), 200

@app.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'start_date': quiz.start_date.isoformat(),
        'end_date': quiz.end_date.isoformat(),
        'time_duration': quiz.time_duration,
        'status': quiz.status,
        'chapter_id': quiz.chapter_id
    }), 200

@app.route('/quizzes/<int:quiz_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_quiz(quiz_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(quiz)
            db.session.commit()
            return jsonify({"message": "Quiz deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # PUT method
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ['title', 'start_date', 'end_date', 'time_duration']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        # Parse dates from ISO format
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        
        if start_date >= end_date:
            return jsonify({"error": "End date must be after start date"}), 400
        
        time_duration = int(data['time_duration'])
        if time_duration <= 0:
            return jsonify({"error": "Time duration must be a positive number of minutes"}), 400
        
        quiz.title = data['title']
        quiz.description = data.get('description', quiz.description)
        quiz.start_date = start_date
        quiz.end_date = end_date
        quiz.time_duration = time_duration
        quiz.status = data.get('status', quiz.status)
        
        db.session.commit()
        return jsonify({"message": "Quiz updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": "Invalid date format or time duration. Please check your input."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/available-quizzes', methods=['GET'])
@jwt_required()
def get_available_quizzes():
    current_user = get_jwt_identity()
    now = datetime.utcnow()
    
    # Get all active quizzes that the user hasn't attempted yet
    attempted_quiz_ids = [score.quiz_id for score in Score.query.filter_by(user_id=current_user['id']).all()]
    
    available_quizzes = []
    quizzes = Quiz.query.filter(
        Quiz.id.notin_(attempted_quiz_ids),
        Quiz.status == 'active',
        Quiz.start_date <= now,
        Quiz.end_date >= now
    ).all()
    
    for quiz in quizzes:
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        available_quizzes.append({
            'id': quiz.id,
            'title': quiz.title,
            'subject': subject.name,
            'chapter': chapter.name,
            'start_date': quiz.start_date.isoformat(),
            'end_date': quiz.end_date.isoformat(),
            'time_duration': quiz.time_duration,
            'total_questions': len(quiz.questions)
        })
    
    return jsonify(available_quizzes), 200

@app.route('/quizzes/<int:quiz_id>/attempt', methods=['POST'])
@jwt_required()
def attempt_quiz(quiz_id):
    current_user = get_jwt_identity()
    
    # Check if quiz exists and is active
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.is_active:
        return jsonify({"error": "This quiz is not currently active"}), 400
    
    # Check if user has already attempted this quiz
    existing_attempt = Score.query.filter_by(
        quiz_id=quiz_id,
        user_id=current_user['id']
    ).first()
    
    if existing_attempt:
        return jsonify({"error": "You have already attempted this quiz"}), 400

    data = request.get_json()
    if not data.get('answers'):
        return jsonify({"error": "No answers provided"}), 400
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    correct_answers = 0
    
    # Calculate score
    for question in questions:
        user_answer = data['answers'].get(str(question.id))
        if user_answer and user_answer == question.correct_option:
            correct_answers += 1
    
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    score = Score(
        quiz_id=quiz_id,
        user_id=current_user['id'],
        total_scored=correct_answers,
        total_questions=total_questions
    )
    
    try:
        db.session.add(score)
        db.session.commit()
        return jsonify({
            "message": "Quiz submitted successfully",
            "score": f"{correct_answers}/{total_questions}",
            "percentage": round(percentage, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Question Routes
@app.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
@jwt_required()
def manage_questions(quiz_id):
    if request.method == 'POST':
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['question_statement', 'option1', 'option2', 'option3', 'option4', 'correct_option']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        try:
            correct_option = int(data['correct_option'])
            if not 1 <= correct_option <= 4:
                return jsonify({"error": "Correct option must be between 1 and 4"}), 400
            
            new_question = Question(
                quiz_id=quiz_id,
                question_statement=data['question_statement'],
                option1=data['option1'],
                option2=data['option2'],
                option3=data['option3'],
                option4=data['option4'],
                correct_option=correct_option
            )
            db.session.add(new_question)
            db.session.commit()
            return jsonify({"message": "Question added successfully"}), 201
        except ValueError:
            return jsonify({"error": "Correct option must be a number between 1 and 4"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # GET method
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([{
        'id': q.id,
        'question_statement': q.question_statement,
        'option1': q.option1,
        'option2': q.option2,
        'option3': q.option3,
        'option4': q.option4,
        'correct_option': q.correct_option if get_jwt_identity()['role'] == 'admin' else None
    } for q in questions]), 200

# User Score Routes
@app.route('/my-scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    current_user = get_jwt_identity()
    scores = Score.query.filter_by(user_id=current_user['id']).all()
    
    score_data = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        score_data.append({
            'subject': subject.name,
            'chapter': chapter.name,
            'quiz_title': quiz.title,
            'score': f"{score.total_scored}/{score.total_questions}",
            'percentage': (score.total_scored / score.total_questions) * 100,
            'attempt_time': score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(score_data), 200

@app.route('/admin/dashboard-stats', methods=['GET'])
@jwt_required()
@cache.cached(timeout=180)
def get_dashboard_stats():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        # Get total subjects
        total_subjects = Subject.query.count()
        
        # Get total chapters
        total_chapters = Chapter.query.count()
        
        # Get active quizzes
        now = datetime.utcnow()
        active_quizzes = Quiz.query.filter(
            Quiz.status == 'active',
            Quiz.start_date <= now,
            Quiz.end_date >= now
        ).count()
        
        # Get total users (excluding admin)
        total_users = User.query.filter(User.role != 'admin').count()
        
        # Get latest subject
        latest_subject = Subject.query.order_by(Subject.id.desc()).first()
        latest_subject_data = None
        if latest_subject:
            latest_subject_data = {
                'id': latest_subject.id,
                'name': latest_subject.name
            }
        
        # Get latest chapter
        latest_chapter = Chapter.query.order_by(Chapter.id.desc()).first()
        latest_chapter_data = None
        if latest_chapter:
            latest_chapter_data = {
                'id': latest_chapter.id,
                'name': latest_chapter.name
            }
        
        # Get recent activity
        recent_scores = Score.query.order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
        recent_activity = []
        
        for score in recent_scores:
            user = User.query.get(score.user_id)
            quiz = Quiz.query.get(score.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            
            recent_activity.append({
                'id': score.id,
                'icon': 'fas fa-check-circle text-success',
                'text': f"{user.full_name} completed quiz '{quiz.title}' with score {score.total_scored}/{score.total_questions}",
                'timestamp': score.time_stamp_of_attempt.isoformat()
            })
        
        return jsonify({
            'stats': {
                'subjects': total_subjects,
                'chapters': total_chapters,
                'activeQuizzes': active_quizzes,
                'users': total_users
            },
            'latestSubject': latest_subject_data,
            'latestChapter': latest_chapter_data,
            'recentActivity': recent_activity
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/statistics', methods=['GET'])
@jwt_required()
@cache.cached(timeout=180)
def get_admin_statistics():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        # Get various statistics
        total_users = User.query.filter(User.role != 'admin').count()
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()
        total_attempts = Score.query.count()

        # Get quiz completion rate
        active_quizzes = Quiz.query.filter(Quiz.status == 'active').count()
        completed_quizzes = Quiz.query.filter(Quiz.status == 'expired').count()
        
        # Get average scores by subject
        subjects_data = []
        subjects = Subject.query.all()
        for subject in subjects:
            chapters = Chapter.query.filter_by(subject_id=subject.id).all()
            chapter_ids = [chapter.id for chapter in chapters]
            quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
            quiz_ids = [quiz.id for quiz in quizzes]
            scores = Score.query.filter(Score.quiz_id.in_(quiz_ids)).all()
            
            if scores:
                avg_score = sum(score.total_scored / score.total_questions * 100 for score in scores) / len(scores)
            else:
                avg_score = 0
                
            subjects_data.append({
                'name': subject.name,
                'average_score': round(avg_score, 2)
            })

        stats = {
            "total_users": total_users,
            "total_subjects": total_subjects,
            "total_chapters": total_chapters,
            "total_quizzes": total_quizzes,
            "total_questions": total_questions,
            "total_attempts": total_attempts,
            "active_quizzes": active_quizzes,
            "completed_quizzes": completed_quizzes,
            "subjects_performance": subjects_data
        }

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/statistics', methods=['GET'])
@jwt_required()
def get_user_statistics():
    current_user = get_jwt_identity()
    try:
        # Get user's quiz attempts
        user_scores = Score.query.filter_by(user_id=current_user['id']).all()
        
        # Calculate total attempts and average score
        total_attempts = len(user_scores)
        if total_attempts > 0:
            average_score = sum(score.total_scored / score.total_questions * 100 for score in user_scores) / total_attempts
        else:
            average_score = 0
        
        # Get performance by subject
        subjects_data = []
        subjects = Subject.query.all()
        for subject in subjects:
            chapters = Chapter.query.filter_by(subject_id=subject.id).all()
            chapter_ids = [chapter.id for chapter in chapters]
            quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
            quiz_ids = [quiz.id for quiz in quizzes]
            scores = Score.query.filter(Score.quiz_id.in_(quiz_ids), Score.user_id == current_user['id']).all()
            
            if scores:
                avg_score = sum(score.total_scored / score.total_questions * 100 for score in scores) / len(scores)
                attempts = len(scores)
            else:
                avg_score = 0
                attempts = 0
                
            subjects_data.append({
                'name': subject.name,
                'average_score': round(avg_score, 2),
                'attempts': attempts
            })
        
        # Get recent performance trend (last 5 attempts)
        recent_scores = Score.query.filter_by(user_id=current_user['id']).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
        performance_trend = []
        for score in recent_scores:
            quiz = Quiz.query.get(score.quiz_id)
            performance_trend.append({
                'quiz_title': quiz.title,
                'score': round((score.total_scored / score.total_questions * 100), 2),
                'date': score.time_stamp_of_attempt.strftime('%Y-%m-%d')
            })

        stats = {
            "total_attempts": total_attempts,
            "average_score": round(average_score, 2),
            "subjects_performance": subjects_data,
            "performance_trend": performance_trend
        }

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)