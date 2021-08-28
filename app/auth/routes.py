from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, DeleteAccountForm
from app.models import User
from app import bcrypt

from app.ApiSettingsDB import ApiSettingsDB


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_data.index'))
    form = LoginForm()
    if form.validate_on_submit():
        with ApiSettingsDB(current_app.config) as db:
            user_info = db.get_user_info(form.username.data)

        if user_info is not None:
            user = User(user_id=user_info[0], username=user_info[1], password_hash=user_info[2])
        else:
            user = None

        if user is None or not bcrypt.check_password_hash(user.password_hash, form.password.data):
            flash('Неправильное имя пользователя или пароль')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_data.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_data.index'))


def create_users_list():
    users_list = []

    with ApiSettingsDB(current_app.config) as db:
        users_data = db.get_users()

    if users_data is None:
        return None

    for user in users_data:
        users_list.append({
            'user_id': user[0],
            'username': user[1]
        })
    return users_list


@bp.route('/accounts_list')
@login_required
def accounts_list():
    users_list = create_users_list()
    if users_list is None:
        flash('Ошибка доступа к списку аккаунтов')
        return render_template('accounts_list.html', title='Список аккаунтов')

    return render_template('accounts_list.html', title='Список аккаунтов', users_table=users_list)


@bp.route('/add_account', methods=['GET', 'POST'])
@login_required
def add_account():
    form = RegistrationForm()

    users_list = create_users_list()
    if users_list is None:
        flash('Ошибка доступа к списку аккаунтов')

    if form.validate_on_submit():
        with ApiSettingsDB(current_app.config) as db:
            user_info = db.get_user_info(form.username.data)
            if user_info is not None:
                flash('Пожалуйста используйте другое имя пользователя')
            else:
                pw_hash = bcrypt.generate_password_hash(form.password.data)
                db.add_user(form.username.data, pw_hash.decode("utf8"))

                users_list = create_users_list()
                flash('Аккаунт успешно добавлен')
    return render_template('add_account.html', title='Добавление аккаунтов', form=form, users_table=users_list)


@bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()

    users_list = create_users_list()
    if users_list is None:
        flash('Ошибка доступа к списку аккаунтов')

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_account.html', title='Удаление аккаунтов', form=form, users_table=users_list)

        with ApiSettingsDB(current_app.config) as db:
            user_info = db.get_user_by_id(form.user_id.data)
            if user_info is None:
                flash('Аккаунта с таким ID не существует')
                return render_template('delete_account.html', title='Удаление аккаунтов', form=form,
                                       users_table=users_list)

            if form.user_id.data == current_user.get_user_id():
                flash('Невозможно удалить аккаунт текущего пользователя')
                return render_template('delete_account.html', title='Удаление аккаунтов', form=form,
                                       users_table=users_list)
            else:
                db.delete_user(form.user_id.data)

                users_list = create_users_list()
                flash('Аккаунт успешно удалён')
    return render_template('delete_account.html', title='Удаление аккаунтов', form=form, users_table=users_list)