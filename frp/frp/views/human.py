# -*- coding: utf-8 -*-
import os

from flask import render_template, request, session, g, abort, flash, url_for, redirect, send_from_directory, send_file
from flask import make_response, jsonify
from werkzeug import secure_filename

from .. import app
from .. import models
from ..models import db
from ..forms import CategoryForm, CampaignForm
from ..helpers import allowed_file


@app.errorhandler(404)
def http_404(error):
    if 'text/html' in request.headers.get("Accept", ""):
        return render_template('404.html',
                               error = error, error_description = "", error_uri = "")
    else:
        return make_response(jsonify({'error' : str(error)}), 404)



@app.route("/")
def index():
    return "Foo"
    products = models.Campaign.query.order_by(models.Campaign.id.desc())
    categories = models.Category.query.order_by(models.Category.id.desc())
    nproducts = models.Campaign.query.count()
    return render_template('index.html',
                           products = products,
                           categories = categories,
                           nproducts = nproducts)

# @app.route("/campaign/add", methods=['GET', 'POST'])
# @lastuser.requires_login
# def campaign_add():
#     form = CampaignForm()
#     if request.method == "POST":
#         if form.validate_on_submit():
#             campaign = models.Campaign()
#             form.populate_obj(campaign)
#             campaign.created_by = g.user
#             db.session.add(campaign)
#             db.session.commit()
#             flash("%s added to campaign list"%form.name.data)
#             return redirect("/")

#     return render_template("create_campaign.html", form = form)

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    return {'scope': 'id email'}


@app.route('/login/redirect')
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect("/")


@app.route('/logout')
def logout():
    flash("You are now logged out", category='info')
    return "/"


@app.route("/campaign/add", methods=['GET', 'POST'])
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
            userid = g.lastuserinfo.userid # Remove from cache
            data = cache.delete(userid)
            return redirect("/")
        else:
            print form.errors
            return render_template('create_campaign.html',
                                   form = form)
    else:
        userid = g.lastuserinfo.userid
        data = cache.get(userid)
        form = CampaignForm(data = data)
        return render_template("create_campaign.html",
                               form = form)
