# Copyright 2017 Twin Tech Labs. All rights reserved

from flask import Blueprint, redirect, render_template, current_app, jsonify
from flask import request, url_for, flash, send_from_directory, jsonify, render_template_string
from flask_user import current_user, login_required, roles_accepted

from slicing_pie_manager import db
from slicing_pie_manager.models.user_models import UserProfileForm, User, Role, UsersRoles, Contribution, ContributionStatus, ContributionForm, WorkRate, WorkRateForm
import uuid, json, os
import datetime

# When using a Flask app factory we must use a blueprint to avoid needing 'app' for '@app.route'
main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/')
def member_page():
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))
    work_rates = WorkRate.query.all()
    contributions = Contribution.query.order_by(Contribution.contribution_date.desc()).all()
    return render_template('pages/member_base.html', work_rates=work_rates, contributions=contributions)


@main_blueprint.route('/contributions', methods=['GET', 'POST'])
@login_required
def manage_contribution_page():
    form = ContributionForm(request.form)
    form.work_rate.choices = [(rate.id, rate.category) for rate in WorkRate.query.all()]
    form.role.choices = [(group.id, group.name) for group 
                         in Role.query.filter(Role.name != "admin", Role.name != "chair").all()]
    contributions = (Contribution.query.filter(Contribution.user_id == current_user.id)
                                      .order_by(Contribution.contribution_date.desc()).all())

    if request.method == 'POST' and form.validate():
        contribution = Contribution(
            user_id=current_user.id, 
            task=form.task.data,
            work_rate_id=form.work_rate.data,
            role_id=form.role.data,
            hours_spent=form.hours_spent.data, 
            cash_spent=form.cash_spent.data, 
            contribution_date=form.contribution_date.data)
        db.session.add(contribution)
        db.session.commit()
        return redirect(url_for('main.manage_contribution_page'))
    return render_template('pages/manage_contributions.html', form=form, contributions=contributions)


@main_blueprint.route('/contributions/<contribution_id>', methods=['POST'])
@login_required
def edit_contribution(contribution_id):
    data = request.form.to_dict()
    contribution = (Contribution.query.filter(
        Contribution.id == contribution_id, 
        current_user.id == Contribution.user_id,
        Contribution.status == ContributionStatus.PROPOSED.value)
        .update(
            dict(
                task=data['task'],
                work_rate_id=data['work_rate'],
                role_id=data['role'],
                hours_spent=data['hours_spent'],
                cash_spent=data['cash_spent'],
                contribution_date=datetime.datetime.strptime(data['contribution_date'], "%Y-%m-%d %H:%M:%S")
            )
        )
    )
    db.session.commit()
    return  redirect(url_for('main.manage_contribution_page'))

@main_blueprint.route('/contributions/delete/<contribution_id>', methods=['POST'])
@login_required
def delete_contribution(contribution_id):
    contribution = (Contribution.query.filter(
        Contribution.id == contribution_id, 
        current_user.id == Contribution.user_id,
        Contribution.status == ContributionStatus.PROPOSED.value)
        .delete()
    )
    db.session.commit()
    return  redirect(url_for('main.manage_contribution_page'))


@main_blueprint.route('/contributions/review', methods=['GET', 'POST'])
@roles_accepted('chair')
def review_contributions_page():
    working_group_roles = ([role.id for role in current_user.roles 
                            if role.name != "admin" and role.name != "chair"])
    print(working_group_roles)
    pending_contributions = (Contribution.query.filter(
        Contribution.role_id.in_(working_group_roles), 
        Contribution.status == ContributionStatus.PROPOSED.value).all())
    print(pending_contributions)
    return render_template('pages/review_contributions.html', 
                           pending_contributions=pending_contributions)


@main_blueprint.route('/contributions/review/approve/<contribution_id>', methods=['POST'])
@roles_accepted('chair')
def approve_contribution(contribution_id):
    contribution = (Contribution.query.filter(
        Contribution.id == contribution_id, 
        Contribution.status == ContributionStatus.PROPOSED.value)
        .update(
            dict(
                status=ContributionStatus.APPROVED.value
            )
        )
    )
    db.session.commit()
    return redirect(url_for('main.review_contributions_page'))


@main_blueprint.route('/contributions/review/deny/<contribution_id>', methods=['POST'])
@roles_accepted('chair')
def deny_contribution(contribution_id):
    contribution = (Contribution.query.filter(
        Contribution.id == contribution_id, 
        Contribution.status == ContributionStatus.PROPOSED.value)
        .update(
            dict(
                status=ContributionStatus.DENIED.value
            )
        )
    )
    db.session.commit()
    return redirect(url_for('main.review_contributions_page'))


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_accepted('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('pages/admin_page.html')

@main_blueprint.route('/users')
@roles_accepted('admin')
def user_admin_page():
    users = User.query.all()
    return render_template('pages/admin/users.html',
        users=users)

@main_blueprint.route('/create_user', methods=['GET', 'POST'])
@roles_accepted('admin')
def create_user_page():
    form = UserProfileForm(request.form, obj=current_user)

    if request.method == 'POST':
        user = User.query.filter(User.email == request.form['email']).first()
        if not user:
            user = User(email=request.form['email'],
                        first_name=request.form['first_name'],
                        last_name=request.form['last_name'],
                        password=current_app.user_manager.hash_password(request.form['password']),
                        active=True,
                        confirmed_at=datetime.datetime.utcnow())
            db.session.add(user)
            db.session.commit()
        return redirect(url_for('main.user_admin_page'))
    return render_template('pages/admin/create_user.html',
                           form=form)

@main_blueprint.route('/delete_user', methods=['GET'])
@roles_accepted('admin')
def delete_user_page():
    try:
        user_id = request.args.get('user_id')

        db.session.query(UsersRoles).filter_by(user_id = user_id).delete()
        db.session.query(User).filter_by(id = user_id).delete()
        db.session.commit()

        flash('You successfully deleted your user!', 'success')
        return redirect(url_for('main.user_admin_page'))
    except Exception as e:
        flash('Opps!  Something unexpected happened.  On the brightside, we logged the error and will absolutely look at it and work to correct it, ASAP.', 'error')
        return redirect(request.referrer)


@main_blueprint.route('/create_work_rate', methods=['GET', 'POST'])
@roles_accepted('admin')
def create_work_rate_page():
    form = WorkRateForm(request.form)
    if request.method == 'POST' and form.validate():
        work_rate = WorkRate.query.filter(WorkRate.category == form.category.data).first()
        if not work_rate:
            work_rate = WorkRate(category=form.category.data,
                        slices_per_hour=form.slices_per_hour.data)
            db.session.add(work_rate)
            db.session.commit()
            return redirect(url_for('main.member_page'))
    return render_template('pages/admin/create_work_rate.html',
                           form=form)


@main_blueprint.route('/pages/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.user_profile_page'))

    # Process GET or invalid POST
    return render_template('pages/user_profile_page.html',
                           current_user=current_user,
                           form=form)
