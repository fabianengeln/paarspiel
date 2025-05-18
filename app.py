from flask import Flask, request, jsonify
from flask_session import Session
from datetime import timedelta
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_NAME'] = 'paarspiel_session'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

Session(app)

db = SQLAlchemy(app)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    used = db.Column(db.Boolean, default=False)

class MiniTask(db.Model):
    __tablename__ = 'mini_tasks'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    used = db.Column(db.Boolean, default=False)

class Compliment(db.Model):
    __tablename__ = 'compliments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    used = db.Column(db.Boolean, default=False)

@app.route('/get_content')
def get_content():
    content_type = request.args.get('type', 'question')
    category = request.args.get('category', 'all')
    
    # Get all items of the requested type
    items = []
    if content_type == 'question':
        items = Question.query.filter_by(used=False).all()
    elif content_type == 'mini_task':
        items = MiniTask.query.filter_by(used=False).all()
    elif content_type == 'compliment':
        items = Compliment.query.filter_by(used=False).all()
    
    # If no unused items are available, reset all items to unused
    if not items:
        if content_type == 'question':
            Question.query.update({Question.used: False})
            items = Question.query.all()
        elif content_type == 'mini_task':
            MiniTask.query.update({MiniTask.used: False})
            items = MiniTask.query.all()
        elif content_type == 'compliment':
            Compliment.query.update({Compliment.used: False})
            items = Compliment.query.all()
        db.session.commit()
    
    # Filter by category if specified
    if category != 'all':
        items = [item for item in items if item.category == category]
    
    # If still no items after category filter, get all items of that category
    if not items:
        if content_type == 'question':
            items = Question.query.filter_by(category=category).all()
        elif content_type == 'mini_task':
            items = MiniTask.query.filter_by(category=category).all()
        elif content_type == 'compliment':
            items = Compliment.query.filter_by(category=category).all()
    
    # Randomly select an item
    if items:
        selected_item = random.choice(items)
        selected_item.used = True
        db.session.commit()
        
        return jsonify({
            'id': selected_item.id,
            'text': selected_item.text,
            'type': content_type,
            'category': selected_item.category
        })
    
    return jsonify({'error': 'No content available'}), 404 