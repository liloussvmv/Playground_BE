from flask import Flask,jsonify,request,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from DB_config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'.format(**db_config)
app.secret_key = 'MyS3cR3tK3y@0b9'
db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    return "<H1> Hello World !!</H1>"


login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

#Table creation
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    hashed_password = generate_password_hash(password, method='sha256')
    user = User.query.filter_by(username=username).first()
    if not user:
        if username and password and email :
            new_user = User(username=username, password=hashed_password,email=email)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'User registered successfully.'}), 201
        else:
            return jsonify({'message': 'Invalid username or password.'}), 400
    else:
        return jsonify({'message': 'Username is taken.'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Invalid username or password.'}), 400
    
    """user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({'message': 'Invalid username or password.'}), 400"""
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password.'}), 400
    
    login_user(user)
    session.permanent = True
    return jsonify({'message': 'User logged in successfully.'}), 200
    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'User logged out successfully.'}), 200

@app.route('/protected')
@login_required
def prot():
    return jsonify({'message': 'Protected.'}), 200

if __name__ == '__main__':
    
    app.run(debug=True)


with app.app_context():
    db.create_all()


# Creating Posts
@app.route('/api/addpost', methods=["POST"])
@login_required
def add_posts():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    user_id = current_user.id

    if title and content:
        new_post = Post(title=title,content=content,user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'message': 'Post Added successfully.'}), 201
    else:
        return jsonify({'message': 'Post Has not been added.'}), 400

# Getting posts from database
@app.route('/api/posts', methods=["GET"])
def get_posts():
    posts = Post.query.all()
    posts_list = []
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "user_id": post.user_id,
            "comments_count": len(post.comments)
        }
        posts_list.append(post_data)
    return jsonify(posts_list)




@app.route('/api/posts/<int:post_id>', methods=["GET"])
def get_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return jsonify({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "user_id": post.user_id
        }), 200
    else:
        return jsonify({'message': 'Post not found.'}), 404
    

@app.route('/api/deletepost/<int:post_id>', methods=["DELETE"])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    current_user_id = current_user.id
    loggedinuser = Post.query.filter(and_(Post.user_id == current_user_id, Post.id == post_id)).first()
    if loggedinuser:
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'message': 'Post Deleted'}), 200
        else:
            return jsonify({'message': 'Post not found.'}), 404
    else: 
        return jsonify({'message': 'Unauthorized.'}), 403

#Adding a comment
   
@app.route('/api/posts/<int:post_id>/comment', methods=["POST"])
def add_comment(post_id):
    data = request.get_json()
    content = data.get("content")
    user_id = current_user.id
    if user_id and content and post_id:
        new_comment = Comment(content=content,user_id=user_id,created_at = "2023-04-29 20:12:27",post_id = post_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'message': 'Comment Added successfully.'}), 201
    else:
        return jsonify({'message': 'Comment Has not been added.'}), 400




"""
@app.route('/api/users')
def get_users():
    users = [
        {'title': 'User 1', 'content': 'This is the User 1.'},
        {'title': 'User 2', 'content': 'This is the User 2.'},
        {'title': 'User 3', 'content': 'This is the User 3.'},
    ]
    return {'Users': users}
"""