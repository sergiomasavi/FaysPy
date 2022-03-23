"""
Main endpoints
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Role
from .forms import EditProfileAdminForm, EditProfileForm
from ..decorators import admin_required

@main.route('/')
def index():
    return render_template('index.html') #'Hello World!', 200

@main.route('/home')
def home():
    return render_template('home.html') #'Hello World!', 200

@main.route('/user/<username>')
def user(username):
    user = db.session.query(User).filter_by(username=username).first() # 404 if user is not found
    if not user:
        return render_template('404.html')

    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)