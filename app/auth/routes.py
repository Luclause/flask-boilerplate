from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import get_locale
from werkzeug.urls import url_parse
from datetime import datetime
from guess_language import guess_language
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Post
from app.translate import translate


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    # Form to submit new posts
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''

        post = Post(
            body=form.post.data,
            author=current_user,
            language=language
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('auth.index'))

    # Get post of followed users
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('auth.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('iauth.ndex', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Home Page', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect user if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    # Otherwise allow user to login
    form = LoginForm()

    # Login logic
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        # Update DB
        db.session.add(user)
        db.session.commit()

        # Print message and exit
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.index'))

    return render_template('register.html', title='Register', form=form)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('auth.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('auth.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None

    form = EmptyForm()

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url,
                           prev_url=prev_url, form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    # Find and set language locale
    g.locale = str(get_locale())


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('auth.index'))

        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('auth.user', username=username))

        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')

        return redirect(url_for('auth.user', username=username))

    else:
        return redirect(url_for('auth.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('auth.index'))

        if user == current_user:
            flash('You can\'t unfollow yourself!')
            return redirect(url_for('auth.user', username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username} anymore.')
        return redirect(url_for('auth.user', username=username))

    else:
        return redirect(url_for('auth.index'))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )

    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))

    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.heml', form=form)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify(
        {'text': translate(
            request.form['text'],
            request.form['source_language'],
            request.form['dest_language']
        )}
    )