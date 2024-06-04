from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, User, Post, Comment, ContactMessage  # Import ContactMessage model
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from forms import LoginForm, EditPostForm, CommentForm, ContactForm  # Import the forms
from flask_wtf.csrf import CSRFProtect
from forms import CreatePostForm
from forms import RegisterForm
from forms import ProfileForm

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object('config.Config')  # Load configuration from config.py
db.init_app(app)  # Initialize SQLAlchemy with the app
csrf = CSRFProtect(app)  # Initialize CSRF protection
login_manager = LoginManager(app)  # Initialize Flask-Login
login_manager.login_view = 'login'  # Set the login view

# User loader callback function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the homepage
@app.route('/')
def index():
    posts = Post.query.all()  # Retrieve all posts from the database
    contact_form = ContactForm()  # Initialize the contact form
    return render_template('index.html', posts=posts, form=contact_form)

# Route to display a single post and handle comments
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    comments = Comment.query.filter_by(post_id=post.id).all()  # Retrieve all comments for the post
    form = CommentForm()  # Initialize the comment form
    if form.validate_on_submit():  # If the form is submitted and valid
        content = form.content.data  # Get the content of the comment
        new_comment = Comment(content=content, author=current_user, post_id=post.id)  # Create a new comment
        db.session.add(new_comment)  # Add the comment to the session
        db.session.commit()  # Commit the session to the database
        return redirect(url_for('post', post_id=post.id))  # Redirect to the post page
    return render_template('post.html', post=post, comments=comments, form=form)

# Route to handle user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Initialize the registration form
    if form.validate_on_submit():  # If the form is submitted and valid
        username = form.username.data  # Get the username
        email = form.email.data  # Get the email
        password = form.password.data  # Get the password
        user = User(username=username, email=email)  # Create a new user
        user.set_password(password)  # Set the user's password
        db.session.add(user)  # Add the user to the session
        db.session.commit()  # Commit the session to the database
        flash('User registered successfully.', 'success')  # Flash a success message
        return redirect(url_for('login'))  # Redirect to the login page
    return render_template('register.html', form=form)

# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Initialize the login form
    if form.validate_on_submit():  # If the form is submitted and valid
        email = form.email.data  # Get the email
        password = form.password.data  # Get the password
        user = User.query.filter_by(email=email).first()  # Retrieve the user by email
        if user and user.check_password(password):  # Check if the user exists and the password is correct
            login_user(user)  # Log in the user
            flash('Logged in successfully.', 'success')  # Flash a success message
            return redirect(url_for('index'))  # Redirect to the homepage
        else:
            flash('Invalid email or password.', 'danger')  # Flash an error message
    return render_template('login.html', form=form)

# Route to handle user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    flash('You have been logged out.', 'info')  # Flash an info message
    return redirect(url_for('login'))  # Redirect to the login page

# Route to display and update the user profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()  # Initialize the profile form
    if form.validate_on_submit():  # If the form is submitted and valid
        current_user.username = form.username.data  # Update the username
        current_user.email = form.email.data  # Update the email
        current_user.address = form.address.data  # Update the address
        current_user.phone_number = form.phone_number.data  # Update the phone number
        if form.password.data:
            current_user.set_password(form.password.data)  # Update the password if provided
        if form.profile_picture.data:
            file = form.profile_picture.data  # Get the profile picture file
            filename = secure_filename(file.filename)  # Secure the filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save the file to the upload folder
            current_user.profile_picture = filename  # Update the profile picture filename
        db.session.commit()  # Commit the session to the database
        flash('Profile updated successfully.', 'success')  # Flash a success message
        return redirect(url_for('profile'))  # Redirect to the profile page
    return render_template('profile.html', form=form)

# Route to create a new post
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreatePostForm()  # Initialize the create post form
    if form.validate_on_submit():  # If the form is submitted and valid
        title = form.title.data  # Get the title
        content = form.content.data  # Get the content
        new_post = Post(title=title, content=content, author=current_user)  # Create a new post
        db.session.add(new_post)  # Add the post to the session
        db.session.commit()  # Commit the session to the database
        flash('Post created successfully.', 'success')  # Flash a success message
        return redirect(url_for('index'))  # Redirect to the homepage
    return render_template('create.html', form=form)

# Route to edit an existing post
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    if post.author != current_user:  # Check if the current user is the author of the post
        flash('You do not have permission to edit this post.', 'danger')  # Flash an error message
        return redirect(url_for('index'))  # Redirect to the homepage

    form = EditPostForm()  # Initialize the edit post form
    if form.validate_on_submit():  # If the form is submitted and valid
        post.title = form.title.data  # Update the title
        post.content = form.content.data  # Update the content
        db.session.commit()  # Commit the session to the database
        flash('Post updated successfully.', 'success')  # Flash a success message
        return redirect(url_for('post', post_id=post.id))  # Redirect to the post page

    form.title.data = post.title  # Pre-fill the form with the current title
    form.content.data = post.content  # Pre-fill the form with the current content
    return render_template('edit_post.html', form=form, post=post)

# Route to delete a post
@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    if post.author != current_user:  # Check if the current user is the author of the post
        flash('You do not have permission to delete this post.', 'danger')  # Flash an error message
        return redirect(url_for('index'))  # Redirect to the homepage
    db.session.delete(post)  # Delete the post
    db.session.commit()  # Commit the session to the database
    flash('Post deleted successfully.', 'success')  # Flash a success message
    return redirect(url_for('index'))  # Redirect to the homepage

# Route to like a post
@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    post.likes += 1  # Increment the like count
    db.session.commit()  # Commit the session to the database
    return jsonify({'likes': post.likes})  # Return the updated like count as JSON

# Route to dislike a post
@app.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_post(post_id):
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    post.dislikes += 1  # Increment the dislike count
    db.session.commit()  # Commit the session to the database
    return jsonify({'dislikes': post.dislikes})  # Return the updated dislike count as JSON

# Route to add a comment to a post
@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form['content']  # Get the comment content from the form
    new_comment = Comment(content=content, author=current_user, post_id=post_id)  # Create a new comment
    db.session.add(new_comment)  # Add the comment to the session
    db.session.commit()  # Commit the session to the database
    return redirect(url_for('post', post_id=post_id))  # Redirect to the post page

# Route to handle contact form submissions
@app.route('/contact', methods=['POST'])
def contact():
    form = ContactForm()  # Initialize the contact form
    if form.validate_on_submit():  # If the form is submitted and valid
        name = form.name.data  # Get the name
        email = form.email.data  # Get the email
        message = form.message.data  # Get the message
        new_message = ContactMessage(name=name, email=email, message=message)  # Create a new contact message
        db.session.add(new_message)  # Add the message to the session
        db.session.commit()  # Commit the session to the database
        flash('Your message has been sent!', 'success')  # Flash a success message
    else:
        flash('There was an error with your submission.', 'danger')  # Flash an error message
    return redirect(url_for('index'))  # Redirect to the homepage
