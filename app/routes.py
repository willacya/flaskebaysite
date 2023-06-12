from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, EbayForm, \
    SearchSettingsForm, WeddingForm
from app.models import User, Post, Ebay
from app.email import send_password_reset_email, send_ebay_results
from app.ebay import ebay_results


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from app.oauth import OAuthSignIn


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())



@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'), 'info')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('ebay.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ebay'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'info')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('ebay')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('ebay'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, social_id=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'), 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('ebay'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'), 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('ebay'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('ebay'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'), 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    ebay_item = user.ebay_items.order_by(Ebay.id.desc())
    form = EmptyForm()
    return render_template('user.html', title=_('Profile Page'),
                            ebays=ebay_item, form=form, user=user)







@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'), 'info')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('ebay'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username), 'info')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('ebay'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username), 'info')
            return redirect(url_for('ebay'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'), 'info')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username), 'info')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('ebay'))



@app.route('/ebay', methods=['GET', 'POST'])
@login_required
def ebay():
    form = EbayForm()
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if form.submit.data and form.validate():
        item = Ebay(keyword=form.keyword.data, minAmount=form.minAmount.data,
                maxAmount=form.maxAmount.data, author=current_user)
        db.session.add(item)
        db.session.commit()
        flash(_('Item Added'), 'success')

    form2 = SearchSettingsForm()
    if form2.submit2.data and form2.validate():
        user.set_searchSettings(form2.location.data, form2.driveTime.data, form2.deadline.data)
        db.session.commit()
        flash(_('Setting Changed'), 'success')

    ebay_item = user.ebay_items.order_by(Ebay.id.desc())

    form.minAmount.data = 0
    form.maxAmount.data = 200

    form2.location.data = user.location
    form2.driveTime.data = user.driveTime
    form2.deadline.data = user.deadline

    return render_template('ebay.html', title=_('Ebay Listings'),
                            ebays=ebay_item, user = user, form=form, form2=form2)


@app.route('/deleteEbayItem/<keyword>', methods=['GET', 'POST'])
@login_required
def deleteEbayItem(keyword):
    keyword = Ebay.query.filter_by(user_id=current_user.id).filter_by(keyword=keyword).order_by(Ebay.id.desc()).first()
    db.session.delete(keyword)
    db.session.commit()
    flash(_('Item Deleted'), 'danger')
    return redirect(url_for('ebay'))

@app.route('/email_everyone', methods=['GET', 'POST'])
@login_required
def email_everyone():
    if current_user.email == 'andrewwillacy@gmail.com':
        users = User.query.all()
        for user in users:
            keywords = Ebay.query.filter_by(user_id = user.id).order_by(Ebay.id.desc()).all()
            html = ""
            for keyword in keywords:
                listings = ebay_results(keyword)
                listings = "<b>None Found</b>" if len(listings) < 1 else listings
                html += "<h2>" + keyword.keyword + "</h2>" + listings + "<br><br>"
            send_ebay_results(user, html)
        flash(_('Email Sent For All'), 'info')
    return redirect(url_for('ebay'))


@app.route('/boot', methods=['GET', 'POST'])
def boot():
    form = LoginForm()
    if form.validate_on_submit():
        flash(_('Congratulations, you are now a registered user!'), 'info')
        return redirect(url_for('boot'))
    return render_template('boot.html', title=_('Bootstrap Tut'), form=form)









@app.route('/wedding', methods=['GET', 'POST'])
def wedding():
    if current_user.is_authenticated:
        return redirect(url_for('ebay'))
    form = WeddingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'info')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('ebay')
        return redirect(next_page)
    return render_template('wedding.html', title=_('Gajeni & Andrew'), form=form)


from app import login as lm

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))



@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))