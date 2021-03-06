# -*- coding: utf-8 -*-

from flask import (render_template,
                   g,
                   url_for,
                   redirect,
                   session,
                   flash,
                   views,
                   request)
from flask.ext.oauth import OAuth

from .. import app
from .. import cache
from ..forms import (DonorSignupForm,
                     LoginForm,
                     BeneficarySignupForm,
                     ProfileForm,
                     CategoryForm,
                     CampaignForm)
from ..service import signup as signup_service
from ..service import user as user_service
from ..service.decorators import login_required

# Facebook requirements
oauth = OAuth()

facebook = oauth.remote_app(
    'facebook',
    request_token_url=None,
    base_url='https://graph.facebook.com/',
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config.get('FACEBOOK_CONSUMER_KEY'),
    consumer_secret=app.config.get('FACEBOOK_CONSUMER_SECRET'),
    request_token_params={'scope': 'email, '})


@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')


def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)
    session.pop('email', None)


# Signup views
@app.route('/signup')
def signup():
    return render_template('signup.html')


class SignupAsBeneficary(views.MethodView):
    @login_required
    def get(self):
        form = BeneficarySignupForm()
        return render_template('signup_as_beneficary.html', form=form)

    @login_required
    def post(self):
        form = BeneficarySignupForm(request.form)
        if form.validate():
            result = signup_service.create_beneficary(form)
            if not result['error']:
                return redirect(url_for('org_info'))
            else:
                flash('Oops something went wrong, please try again')
        return render_template('signup_as_beneficary.html', form=form)


app.add_url_rule('/signup/beneficary',
                 view_func=SignupAsBeneficary.as_view('signup_as_beneficary'))


class SignupAsBeneficaryTemp(views.MethodView):
    @login_required
    def get(self):
        form = BeneficarySignupForm()
        return render_template('sigup_as_beneficary_old.html', form=form)

    @login_required
    def post(self):
        form = BeneficarySignupForm(request.form)
        if form.validate():
            result = signup_service.create_beneficary(form)
            if not result['error']:
                return redirect(url_for('org_info'))
            else:
                flash('Oops something went wrong, please try again')
        return render_template('sigup_as_beneficary_old.html', form=form)

app.add_url_rule('/signup/beneficarytemp',
                 view_func=SignupAsBeneficaryTemp.as_view('signup_as_beneficarytemp'))


@app.route('/signup/donor', methods=['GET', 'POST'])
def signup_as_donor():
    if request.method == 'GET':
        form = DonorSignupForm()
        return render_template('signup_as_donor.html', form=form)
    elif request.method == 'POST':
        form = DonorSignupForm(request.form)
        if form.validate():
            # Create the new user and create userinfo
            signup_service.create_donor_from_webform(form)
            return redirect(url_for('profile'))
        else:
            return render_template('signup_as_donor.html', form=form)


# Login views
@app.route('/login/facebook', methods=['GET', 'POST'])
def login_via_facebook():
    return facebook.authorize(
        callback=url_for('facebook_authorized',
                         next=request.args.get('next'),
                         _external=True))


@app.route("/login/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')
    data = facebook.get('me')

    signup_service.create_donor_from_facebook(data.data)
    session['email'] = data.data.get('email')
    return redirect(url_for('profile'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/webform', methods=['GET', 'POST'])
def login_via_webform():
    # IF logged in redirect
    if session.get('logged_in'):
        return redirect(url_for('profile'))

    form = LoginForm()
    if request.method == "GET":
        return render_template('login_form.html', form=form)
    elif request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            if user_service.is_valid_login(form.email.data,
                                           form.password.data):
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials')
                return render_template('login_form.html', form=form)
        else:
            return render_template('login_form.html', form=form)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


class EditProfile(views.MethodView):
    @login_required
    def get(self):
        form = ProfileForm()
        # We don't need password, email field
        form.delete_fields('password', 'email')
        form.set_data(g.user)
        return render_template('edit_profile.html', form=form)

    @login_required
    def post(self):
        form = ProfileForm(request.form)
        form.delete_fields('password', 'email')
        if form.validate():
            user_service.update_profile(form)
            return redirect(url_for('profile'))
        return render_template('edit_profile.html', form=form)


app.add_url_rule('/profile/edit',
                 view_func=EditProfile.as_view('edit_profile'))


@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/category/add", methods=['GET', 'POST'])
def category_add():
    form = CategoryForm()
    if request.method == "POST":
        if form.validate_on_submit():
            category = models.Category(name = form.name.data)
            icon = request.files['icon']
            filename = secure_filename(icon.filename)
            if filename and allowed_file(filename):
                full_save_path = os.path.join(app.config['UPLOAD_DIRECTORY'], 'icons', filename)
                icon.save(full_save_path)
                category.icon = filename
            db.session.add(category)
            db.session.commit()
            flash("category %s added"%form.name.data)
            return redirect("/")
    return render_template("create_category.html", form = form)

@app.route("/category/<cat_id>/icon", methods=['GET'])
def category_icon(cat_id):
    category = models.Category.query.filter_by(id = cat_id).first()
    if category and category.icon:
        return send_from_directory(app.config['UPLOAD_DIRECTORY']+"/icons/", category.icon)

@app.route("/partials/<path:page>", methods = ['GET'])
def angular_partials(page):
    return render_template("partials/{}".format(page))

@app.route("/campaign/add", methods=['GET', 'POST'])
@login_required
def campaign_add():
    if request.method == "POST":
        form = CampaignForm()
        if form.validate_on_submit():
            campaign = models.Campaign()
            form.populate_obj(campaign)
            campaign.created_by = g.user
            db.session.add(campaign)
            db.session.commit()
            flash("%s added to campaign list"%form.name.data)
            userid = g.user.username # Remove from cache
            # TBD : implement redis cache
            # data = cache.delete(userid)
            return redirect("/")
        else:
            print form.errors
            return render_template('create_campaign.html',
                                   form = form)
    else:
        userid = g.user.username
        # data = cache.get(userid)
        form = CampaignForm()
        return render_template("create_campaign.html",
                               form = form)

@app.route("/discover", methods=['GET', 'POST'])
def discover():
    return render_template('discover.html')

@app.route("/start", methods=['GET', 'POST'])
def start():
    return render_template('start.html')

@app.route("/campaignPage", methods=['GET', 'POST'])
def campaignPage():
    return render_template('campaignPage.html')
