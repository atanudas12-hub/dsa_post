from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this' # TODO: Change for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leetcode_url = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Validations ---
def validate_leetcode_url(url):
    return "leetcode.com" in url

# --- Routes ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # Public Feed
    user_name = current_user.username if current_user.is_authenticated else None
    return render_template('dashboard.html', name=user_name)

@app.route('/auth')
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('auth.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({'success': True, 'redirect': url_for('index')})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('index')})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Login required'}), 401
            
        data = request.get_json()
        url = data.get('url')
        
        if not url: 
            return jsonify({'success': False, 'message': 'Invalid URL'}), 400
            
        new_post = Post(leetcode_url=url, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Posted!'})
    
    # GET: Fetch all posts (Public)
    all_posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = []
    for post in all_posts:
        posts_data.append({
            'id': post.id,
            'username': post.author.username,
            'url': post.leetcode_url,
            'timestamp': post.timestamp.isoformat()
        })
    return jsonify({'posts': posts_data})

# --- Init DB ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
