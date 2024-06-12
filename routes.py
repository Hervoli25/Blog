from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_socketio import send, emit
from models import db, User, Post, Comment, ContactMessage
from forms import LoginForm, RegisterForm, CreatePostForm, ContactForm, ProfileForm, EditPostForm, CommentForm
from werkzeug.utils import secure_filename
from app import socketio
import os

app = Blueprint('app', __name__)

@app.route('/')
def index():
    posts = Post.query.all()
    contact_form = ContactForm()
    return render_template('index.html', posts=posts, form=contact_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('app.index'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        new_comment = Comment(content=content, author=current_user, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('app.post', post_id=post.id))
    return render_template('post.html', post=post, comments=comments, form=form, author=post.author)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        current_user.phone_number = form.phone_number.data
        if form.password.data:
            current_user.set_password(form.password.data)
        if form.profile_picture.data:
            file = form.profile_picture.data
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))
            current_user.profile_picture = filename
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('app.profile'))
    return render_template('profile.html', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreatePostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_post = Post(title=title, content=content, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully.', 'success')
        return redirect(url_for('app.index'))
    return render_template('create.html', form=form)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('app.index'))
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('app.post', post_id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    return render_template('edit_post.html', form=form, post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('app.index'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('app.index'))

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

@app.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.dislikes += 1
    db.session.commit()
    return jsonify({'dislikes': post.dislikes})

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form['content']
    new_comment = Comment(content=content, author=current_user, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('app.post', post_id=post_id))

@app.route('/contact', methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()
        flash('Your message has been sent!', 'success')
    else:
        flash('There was an error with your submission.', 'danger')
    return redirect(url_for('app.index'))

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot follow yourself!', 'danger')
        return redirect(url_for('app.profile', user_id=user_id))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {user.username}!', 'success')
    return redirect(url_for('app.profile', user_id=user_id))

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot unfollow yourself!', 'danger')
        return redirect(url_for('app.profile', user_id=user_id))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {user.username}!', 'success')
    return redirect(url_for('app.profile', user_id=user_id))

@app.route('/chat')
@login_required
def chat():
    users = User.query.all()
    return render_template('chat.html', users=users)

@app.route('/share/<int:post_id>', methods=['POST'])
@login_required
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    shared_with = request.form.get('shared_with')
    user = User.query.filter_by(username=shared_with).first()
    if user:
        flash(f'Post shared with {user.username}', 'success')
    else:
        flash('User not found', 'danger')
    return redirect(url_for('app.post', post_id=post.id))

@socketio.on('message')
def handle_message(data):
    message = data['message']
    to_user_id = data['to_user']
    from_user = current_user.username

    # Find the recipient user by ID
    to_user = User.query.get(to_user_id)
    if to_user:
        # Emit the message to the recipient
        emit('message', {'message': message, 'from_user': from_user}, room=to_user_id)

    # Optionally, broadcast the message to all users or handle as needed
    emit('message', {'message': message, 'from_user': from_user}, broadcast=True)

@app.route('/policy')
def policy():
    return render_template('policy.html')
