from flask import Blueprint, render_template, flash, current_app

from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from app.scheduledb import ScheduleDB
import re

bp = Blueprint('delete_data', __name__)


class DeleteOrganization(FlaskForm):
    organization = StringField('Введите организацию', validators=[DataRequired(), Length(max=80)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить организацию')


class DeleteFaculty(FlaskForm):
    organization = StringField('Введите организацию', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Введите факультет', validators=[DataRequired(), Length(max=80)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить факультет')


class DeleteGroup(FlaskForm):
    organization = StringField('Введите организацию', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Введите факультет', validators=[DataRequired(), Length(max=80)])
    group = StringField('Введите группу', validators=[DataRequired(), Length(max=50)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить группу')


class DeleteGroupSchedule(FlaskForm):
    organization = StringField('Введите организацию', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Введите факультет', validators=[DataRequired(), Length(max=80)])
    group = StringField('Введите группу', validators=[DataRequired(), Length(max=50)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить расписание занятий')


class DeleteGroupExams(FlaskForm):
    organization = StringField('Введите организацию', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Введите факультет', validators=[DataRequired(), Length(max=80)])
    group = StringField('Введите группу', validators=[DataRequired(), Length(max=50)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить расписание экзаменов')


class DeleteAllSchedule(FlaskForm):
    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить расписание занятий всех групп')


class DeleteAllExams(FlaskForm):
    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить расписание экзаменов всех групп')


class DeleteOldGroups(FlaskForm):
    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить выпустившиеся группы')


@bp.route('/delete_data')
@login_required
def delete_data():
    return render_template('delete_data.html', title='Удаление')


@bp.route('/delete_organization', methods=['GET', 'POST'])
@login_required
def delete_organization():
    form = DeleteOrganization()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_organization.html', title='Удаление организации', form=form)

        organization = form.organization.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db.delete_organization(organization)
            flash('Организация успешно удалена')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_organization: {}'.format(str(e)))
        finally:
            return render_template('delete_organization.html', title='Удаление организации', form=form)
    return render_template('delete_organization.html', title='Удаление организации', form=form)


@bp.route('/delete_faculty', methods=['GET', 'POST'])
@login_required
def delete_faculty():
    form = DeleteFaculty()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_faculty.html', title='Удаление факультета', form=form)

        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db.delete_faculty(organization, faculty)
            flash('Факультет успешно удалён')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_faculty: {}'.format(str(e)))
        finally:
            return render_template('delete_faculty.html', title='Удаление факультета', form=form)
    return render_template('delete_faculty.html', title='Удаление факультета', form=form)


@bp.route('/delete_group', methods=['GET', 'POST'])
@login_required
def delete_group():
    form = DeleteGroup()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_group.html', title='Удаление группы', form=form)

        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db.delete_group(organization, faculty, group)
            flash('Группа успешно удалена')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_group: {}'.format(str(e)))
        finally:
            return render_template('delete_group.html', title='Удаление группы', form=form)
    return render_template('delete_group.html', title='Удаление группы', form=form)


@bp.route('/delete_group_schedule', methods=['GET', 'POST'])
@login_required
def delete_group_schedule():
    form = DeleteGroupSchedule()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_group_schedule.html',
                                   title='Удаление расписания занятий выбранной группы', form=form)

        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db_data = db.get_group(organization, faculty, group)

                if db_data is None:
                    flash('Такой группы нет в базе данных')
                    return render_template('delete_group_schedule.html',
                                           title='Удаление расписания занятий выбранной группы', form=form)

                tag = db_data[1]
                db.delete_schedule(tag)
            flash('Расписание занятий выбранной группы успешно удалено')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_group_schedule: {}'.format(str(e)))
        finally:
            return render_template('delete_group_schedule.html',
                                   title='Удаление расписания занятий выбранной группы', form=form)
    return render_template('delete_group_schedule.html',
                           title='Удаление расписания занятий выбранной группы', form=form)


@bp.route('/delete_group_exams', methods=['GET', 'POST'])
@login_required
def delete_group_exams():
    form = DeleteGroupExams()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_group_exams.html',
                                   title='Удаление расписания экзаменов выбранной группы', form=form)

        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db_data = db.get_group(organization, faculty, group)

                if db_data is None:
                    flash('Такой группы нет в базе данных')
                    return render_template('delete_group_exams.html',
                                           title='Удаление расписания экзаменов выбранной группы', form=form)

                tag = db_data[1]
                db.delete_exams(tag)
            flash('Расписание экзаменов выбранной группы успешно удалено')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_group_exams: {}'.format(str(e)))
        finally:
            return render_template('delete_group_exams.html',
                                   title='Удаление расписания экзаменов выбранной группы', form=form)
    return render_template('delete_group_exams.html',
                           title='Удаление расписания экзаменов выбранной группы', form=form)


@bp.route('/delete_all_schedule', methods=['GET', 'POST'])
@login_required
def delete_all_schedule():
    form = DeleteAllSchedule()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_all_schedule.html',
                                   title='Удаление расписания занятий всех групп', form=form)

        try:
            with ScheduleDB(current_app.config) as db:
                org_data_list = db.get_organizations()
                for db_org_data in org_data_list:
                    org = db_org_data[0]

                    faculty_data_list = db.get_faculty(org)
                    for db_faculty_data in faculty_data_list:
                        faculty = db_faculty_data[0]

                        groups_data_list = db.get_group_list(org, faculty)
                        for db_group_data in groups_data_list:
                            group, tag = db_group_data
                            db.delete_schedule(tag)
            flash('Расписание занятий для всех групп успешно удалено')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_all_schedule: {}'.format(str(e)))
        finally:
            return render_template('delete_all_schedule.html',
                                   title='Удаление расписания занятий всех групп', form=form)
    return render_template('delete_all_schedule.html',
                           title='Удаление расписания занятий всех групп', form=form)


@bp.route('/delete_all_exams', methods=['GET', 'POST'])
@login_required
def delete_all_exams():
    form = DeleteAllSchedule()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_all_exams.html',
                                   title='Удаление расписания экзаменов всех групп', form=form)

        try:
            with ScheduleDB(current_app.config) as db:
                org_data_list = db.get_organizations()
                for db_org_data in org_data_list:
                    org = db_org_data[0]

                    faculty_data_list = db.get_faculty(org)
                    for db_faculty_data in faculty_data_list:
                        faculty = db_faculty_data[0]

                        groups_data_list = db.get_group_list(org, faculty)
                        for db_group_data in groups_data_list:
                            group, tag = db_group_data
                            db.delete_exams(tag)
            flash('Расписание экзаменов для всех групп успешно удалено')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_all_exams: {}'.format(str(e)))
        finally:
            return render_template('delete_all_exams.html',
                                   title='Удаление расписания экзаменов всех групп', form=form)
    return render_template('delete_all_exams.html',
                           title='Удаление расписания экзаменов всех групп', form=form)


def can_be_deleted(faculty_title, group_title):
    group_data = group_title.split('-')

    if len(group_data) == 2:
        result = re.match(r'(\d{1,3})(\w*)', group_data[1])

        if result:
            items = result.groups()

            if len(items) == 2 \
                    and items[0].isdigit() \
                    and 2 <= len(items[0]) <= 3 \
                    and re.fullmatch(r'(\w+ )*\d \w+', faculty_title) is not None:

                if len(items[0]) == 2:
                    semester_number = int(items[0][0])
                elif len(items[0]) == 3:
                    semester_number = int(items[0][:2])
                else:
                    semester_number = 0

                # Бакалавриат
                if items[1] == 'Б' and semester_number > 8:
                    return True

                # Магистратура
                if items[1] == 'М' and semester_number > 4:
                    return True

                # Специалитет
                if not items[1] and semester_number > 12:
                    return True
    return False


@bp.route('/delete_old_groups', methods=['GET', 'POST'])
@login_required
def delete_old_groups():
    form = DeleteOldGroups()

    if form.validate_on_submit():
        if not form.confirm_delete.data:
            flash('Вы не подтвердили удаление')
            return render_template('delete_old_groups.html',
                                   title='Удаление выпустившихся групп', form=form)

        deleted_groups_table = []
        try:
            with ScheduleDB(current_app.config) as db:
                org_data_list = db.get_organizations()
                for db_org_data in org_data_list:
                    org = db_org_data[0]

                    faculty_data_list = db.get_faculty(org)
                    for db_faculty_data in faculty_data_list:
                        faculty = db_faculty_data[0]

                        groups_data_list = db.get_group_list(org, faculty)
                        for db_group_data in groups_data_list:
                            group, tag = db_group_data
                            if can_be_deleted(faculty, group):
                                db.delete_group(org, faculty, group)
                                deleted_groups_table.append({
                                    'organization': org,
                                    'faculty': faculty,
                                    'group': group,
                                    'tag': tag
                                })
            flash('Выпустившиеся группы успешно удалены')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('delete_old_groups: {}'.format(str(e)))
        finally:
            return render_template('delete_old_groups.html',
                                   title='Удаление выпустившихся групп', form=form, deleted_groups_table=deleted_groups_table)
    return render_template('delete_old_groups.html',
                           title='Удаление выпустившихся групп', form=form)
