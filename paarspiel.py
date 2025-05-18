from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import random
import os
from datetime import datetime
from sqlalchemy import func
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF

# Ensure session directory exists
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
Session(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'question', 'task', or 'compliment'
    answers = db.relationship('Answer', backref='question', lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    person_name = db.Column(db.String(100), nullable=False)

# Helper function to read content from a CSV file
def read_content_from_csv(filepath):
    content_list = []
    print(f"Attempting to read CSV file line by line: {filepath}") # Debug log
    if os.path.exists(filepath):
        print(f"File found: {filepath}") # Debug log
        with open(filepath, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    content_list.append(line)
        print(f"Read {len(content_list)} items from {filepath}") # Debug log
    else:
        print(f"File not found: {filepath}") # Debug log
    return content_list

def init_db():
    with app.app_context():
        # Use Flask-SQLAlchemy to create tables (if they don't exist)
        db.create_all()

        # Always clear existing data in Question and Answer tables for fresh start
        db.session.query(Answer).delete()
        db.session.query(Question).delete()
        db.session.commit()
        print("Cleared existing data from Question and Answer tables.") # Debug log

        # Check if questions exist AFTER clearing (should always be None now)
        if Question.query.first() is None:
            print("Database is ready for initialization with content.") # Debug log
            # Load Questions from hardcoded list
            questions = [
                # Kommunikation
                Question(text='Was war ein Missverständnis zwischen euch beiden, das euch zum Lachen gebracht hat?', category='🗣 Kommunikation', type='question'),
                Question(text='In welchen Situationen fühlst du dich am besten verstanden?', category='🗣 Kommunikation', type='question'),
                Question(text='Wie können wir in stressigen Zeiten besser kommunizieren?', category='🗣 Kommunikation', type='question'),
                Question(text='Welches Kommunikationsmuster von mir nervt dich manchmal (sachte formuliert)?', category='🗣 Kommunikation', type='question'),
                Question(text='Wie sprichst du am liebsten über schwierige Themen?', category='🗣 Kommunikation', type='question'),
                Question(text='Was bedeutet achtsame Kommunikation für dich?', category='🗣 Kommunikation', type='question'),
                Question(text='Wie können wir sicherstellen, dass wir uns auch ohne Worte verstehen?', category='🗣 Kommunikation', type='question'),
                Question(text='Wann fühlst du dich in Gesprächen mit mir am sichersten?', category='🗣 Kommunikation', type='question'),
                Question(text='Welche nonverbalen Signale von mir verstehst du am leichtesten?', category='🗣 Kommunikation', type='question'),
                Question(text='Wie gehen wir am besten mit Meinungsverschiedenheiten um?', category='🗣 Kommunikation', type='question'),
                Question(text='Was können wir tun, um unsere Kommunikation im Alltag bewusster zu gestalten?', category='🗣 Kommunikation', type='question'),
                Question(text='Gibt es etwas, das du dir schon immer mal trauen wolltest, mir zu sagen?', category='🗣 Kommunikation', type='question'),

                # Zärtlichkeit & Nähe
                Question(text='Was ist deine Lieblingsart, Zuneigung zu zeigen oder zu empfangen?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Wann hast du dich mir zuletzt besonders nah gefühlt?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Wie können wir mehr zärtliche Momente in unseren Alltag bringen?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Was ist für dich ein perfekter kuscheliger Abend?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Gibt es eine Geste der Zärtlichkeit, die du besonders magst?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Wann hast du dich zuletzt von mir besonders begehrt gefühlt?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Wie wichtig ist dir körperliche Nähe im Vergleich zu emotionaler Nähe?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Welcher Ort ist für dich der Inbegriff von Romantik?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Was ist das Zärtlichste, das jemand je für dich getan hat?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Wie können wir unsere Intimität vertiefen?', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Beschreibe einen Moment, in dem du dich mir ohne Worte nahe gefühlt hast.', category='💞 Zärtlichkeit & Nähe', type='question'),
                Question(text='Was bedeutet Sicherheit und Geborgenheit für dich in unserer Beziehung?', category='💞 Zärtlichkeit & Nähe', type='question'),

                # Alltagsstress & Bedürfnisse
                Question(text='Wie kann ich dich an einem stressigen Tag am besten unterstützen?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Welches Bedürfnis von dir wird im Moment zu wenig erfüllt?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Was hilft dir am besten, um nach einem anstrengenden Tag abzuschalten?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Gibt es etwas, das ich tun oder lassen kann, um deinen Stress zu reduzieren?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Wie äußert sich Stress bei dir und wie erkenne ich das am besten?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Was brauchst du, um dich im Alltag mehr gesehen und wertgeschätzt zu fühlen?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Wie wichtig ist dir Zeit für dich alleine und wie können wir das ermöglichen?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Welche kleinen Dinge im Alltag geben dir Energie?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Gibt es eine Routine, die dir im Alltag fehlt und die wir einführen könnten?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Wie gehst du mit Überforderung um und wie kann ich dir dabei helfen?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Was bedeutet für dich ein unterstützendes Umfeld?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),
                Question(text='Welche Bedürfnisse sind für dich momentan am wichtigsten?', category='🤯 Alltagsstress & Bedürfnisse', type='question'),

                # Gemeinsame Visionen
                Question(text='Was ist ein gemeinsamer Traum, den wir uns in den nächsten Jahren erfüllen wollen?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Wie stellen wir uns unser gemeinsames Leben in 5 Jahren vor?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Welches Abenteuer möchtest du unbedingt noch mit mir erleben?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Was ist uns beiden in Bezug auf unsere gemeinsame Zukunft am wichtigsten?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Gibt es ein Projekt, das wir unbedingt gemeinsam angehen sollten?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Wie können wir unsere individuellen Ziele und unsere gemeinsamen Visionen in Einklang bringen?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Welchen Beitrag möchtest du für die Welt leisten und wie können wir das gemeinsam tun?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Was ist der nächste Meilenstein, den wir als Paar erreichen wollen?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Wie können wir unsere gemeinsame Zeit noch erfüllender gestalten?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Was ist für dich das Wichtigste, das wir als Paar erschaffen können?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Welche Werte sind uns in unserer gemeinsamen Zukunft besonders wichtig?', category='🧭 Gemeinsame Visionen', type='question'),
                Question(text='Wie können wir sicherstellen, dass wir auf dem Weg zu unseren Zielen Spaß haben?', category='🧭 Gemeinsame Visionen', type='question'),

                # Humor & Leichtigkeit
                Question(text='Was war der lustigste Moment, den wir zusammen erlebt haben?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Welche Art von Humor teilen wir am meisten?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Wie können wir mehr Leichtigkeit und Spaß in unseren Alltag bringen?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Gibt es eine alberne Angewohnheit von mir, die du insgeheim magst?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Was bringt dich sofort zum Lachen, egal wie deine Stimmung ist?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Welches Spiel oder welche Aktivität macht uns beiden am meisten Spaß?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Wie können wir auch in ernsten Situationen unseren Humor bewahren?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Was ist die schönste Erinnerung an einen unbeschwerten Moment zusammen?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Gibt es einen Insider-Witz, den nur wir verstehen?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Wie können wir mehr spontane, lustige Momente in unseren Alltag integrieren?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Was bedeutet für dich Leichtigkeit in einer Beziehung?', category='🎭 Humor & Leichtigkeit', type='question'),
                Question(text='Welche Kindheitserinnerung bringt dich immer zum Lachen?', category='🎭 Humor & Leichtigkeit', type='question'),
            ]

            # Load Mini-Tasks from CSV
            mini_tasks_list = read_content_from_csv('mini_tasks.csv')
            mini_tasks = [Question(text=task, category='💝 Mini-Aufgabe', type='mini_task') for task in mini_tasks_list]
            print(f"Created {len(mini_tasks)} mini_task objects.") # Debug log

            # Load Compliments from CSV
            compliments_list = read_content_from_csv('compliments.csv')
            compliments = [Question(text=compliment, category='✨ Kompliment', type='compliment') for compliment in compliments_list]
            print(f"Created {len(compliments)} compliment objects.") # Debug log

            # Combine all content
            all_content = questions + mini_tasks + compliments
            print(f"Total content items to add: {len(all_content)}") # Debug log

            # Add all content to the database using Flask-SQLAlchemy session
            for content_item in all_content:
                db.session.add(content_item)
            db.session.commit()
            print("All content added to database and committed.") # Debug log

@app.before_request
def before_request():
    print("\n=== New Request ===")
    print("Request path:", request.path)
    print("Request method:", request.method)
    print("Session data:", dict(session))
    print("==================\n")
    
    # Make sure session is permanent
    session.permanent = True
    
    # Ensure session data exists for game routes
    if request.path in ['/game', '/switch_turn', '/save_answer']:
        if not session.get('person1') or not session.get('person2') or not session.get('current_turn'):
            print("No session data found, redirecting to home")
            return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('start.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    try:
        person1 = request.form.get('person1')
        person2 = request.form.get('person2')
        
        print(f"Received player names: {person1}, {person2}")  # Debug log
        
        if not person1 or not person2:
            print("Missing player names")  # Debug log
            return redirect(url_for('home'))
        
        # Clear any existing session data
        session.clear()
        
        # Set new session data
        session['person1'] = person1
        session['person2'] = person2
        session['current_turn'] = person1  # Start with person1
        
        # Force session update
        session.modified = True
        
        print(f"Session data set: {dict(session)}")  # Debug log
        
        return redirect(url_for('game'))
    except Exception as e:
        print(f"Error in start_game: {str(e)}")  # Debug log
        return redirect(url_for('home'))

@app.route('/game')
def game():
    try:
        # Check if session data exists
        if 'person1' not in session or 'person2' not in session or 'current_turn' not in session:
            print("Missing session data in game route")  # Debug log
            return redirect(url_for('home'))
            
        print(f"Game route session data: {session}")  # Debug log
        
        return render_template('index.html', 
                             person1=session['person1'], 
                             person2=session['person2'],
                             current_turn=session['current_turn'])
    except Exception as e:
        print(f"Error in game route: {str(e)}")  # Debug log
        return redirect(url_for('home'))

@app.route('/get_content')
def get_content():
    content_type = request.args.get('type', 'question')  # Default to question if no type specified
    category = request.args.get('category', 'all')
    print(f"get_content called with type={content_type} and category={category}") # Debug log

    # Get a random question from the database
    if category == 'all':
        print(f"get_content: Querying for random item of type: {content_type}") # Debug log
        content_item = Question.query.filter_by(type=content_type).order_by(func.random()).first() # Renamed variable to avoid confusion
    else:
        print(f"get_content: Querying for random item of type: {content_type} and category: {category}") # Debug log
        content_item = Question.query.filter_by(category=category, type=content_type).order_by(func.random()).first() # Renamed variable

    if content_item:
        print(f"get_content: Found content item with id={content_item.id}, type={content_item.type}") # Debug log
        return jsonify({
            'id': content_item.id,
            'text': content_item.text,
            'type': content_item.type
        })
    else:
        print(f"get_content: No content found for type={content_type} and category={category}") # Debug log
        return jsonify({
            'id': None,
            'text': 'Kein Content verfügbar',
            'type': content_type
        })

@app.route('/get_categories')
def get_categories():
    content_type = request.args.get('type', 'question')
    categories = db.session.query(Question.category).filter_by(type=content_type).distinct().all()
    return jsonify({'categories': [cat[0] for cat in categories]})

@app.route('/save_answer', methods=['POST'])
def save_answer():
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        answer_text = data.get('answer')
        
        if not all([question_id, answer_text]):
            return jsonify({'status': 'error', 'message': 'Missing data'})
        
        current_turn = session.get('current_turn')
        if not current_turn:
            return jsonify({'status': 'error', 'message': 'No current turn'})
        
        # Save the answer
        answer = Answer(question_id=question_id, text=answer_text, person_name=current_turn)
        db.session.add(answer)
        db.session.commit()
        
        # Switch turns
        person1 = session.get('person1')
        person2 = session.get('person2')
        
        if current_turn == person1:
            session['current_turn'] = person2
        else:
            session['current_turn'] = person1
        
        # Force session update
        session.modified = True
        
        return jsonify({
            'status': 'success',
            'current_turn': session['current_turn'],
            'person1': person1,
            'person2': person2
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/switch_turn', methods=['POST'])
def switch_turn():
    print("\n=== Switch Turn Request ===")
    print("Full session data:", dict(session))
    print("Session type:", type(session))
    print("Session ID:", session.sid if hasattr(session, 'sid') else "No session ID")
    print("Current session state:")
    print("person1:", session.get('person1'))
    print("person2:", session.get('person2'))
    print("current_turn:", session.get('current_turn'))
    
    if not session.get('person1') or not session.get('person2') or not session.get('current_turn'):
        return jsonify({'error': 'Session data missing'}), 400
    
    current_turn = session.get('current_turn')
    person1 = session.get('person1')
    person2 = session.get('person2')
    
    # Determine next turn
    next_turn = person2 if current_turn == person1 else person1
    
    # Update session
    session['current_turn'] = next_turn
    session.modified = True  # Explicitly mark session as modified
    
    print("Turn switched to:", next_turn)
    print("Updated session data:", dict(session))
    print("========================\n")
    
    return jsonify({'success': True, 'current_turn': next_turn})

@app.route('/summary')
def summary():
    answers = db.session.query(Answer, Question).join(Question).order_by(Answer.timestamp.desc()).all()
    return render_template('summary.html', answers=answers)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
