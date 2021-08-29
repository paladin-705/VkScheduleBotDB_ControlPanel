from flask import Blueprint, render_template, flash, current_app

from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.scheduledb import ScheduleDB


bp = Blueprint('show_data', __name__)


class ShowGroupDataForm(FlaskForm):
    organization = StringField('Название организации', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Название факультета', validators=[DataRequired(), Length(max=80)])
    group = StringField('Название группы', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Показать расписание')


@bp.route('/show_data')
@login_required
def show_data():
    return render_template('show_data.html', title='Просмотр данных')


@bp.route('/show_group_list')
@login_required
def show_group_list():
    table_data = []

    with ScheduleDB(current_app.config) as db:
        org_data_list = db.get_organizations()
        for org_data in org_data_list:
            org = org_data[0]
            faculty_data_list = db.get_faculty(org)
            for faculty_data in faculty_data_list:
                faculty = faculty_data[0]
                groups_data_list = db.get_group_list(org, faculty)
                for group_data in groups_data_list:
                    group, tag = group_data
                    table_data.append({
                        'organization': org,
                        'faculty': faculty,
                        'group': group,
                        'tag': tag
                    })

    return render_template('show_group_list.html', title='Список групп', groups_list=table_data)


@bp.route('/show_group_schedule', methods=['GET', 'POST'])
@login_required
def show_group_schedule():
    form = ShowGroupDataForm()

    if form.validate_on_submit():
        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()

        schedule_table = []
        try:
            with ScheduleDB(current_app.config) as db:
                db_data = db.get_group(organization, faculty, group)

                if db_data is None:
                    flash('Группы нет в базе данных')
                    return render_template('show_group_schedule.html',
                                           title='Расписание занятий отдельной группы', form=form)

                tag = db_data[1]
                schedule = db.get_schedule(tag)

            for row in schedule:
                week_type = row[3]
                if week_type == 0:
                    week_type_text = 'odd'
                elif week_type == 1:
                    week_type_text = 'even'
                elif week_type == 2:
                    week_type_text = 'all'
                else:
                    week_type_text = ''

                schedule_table.append({
                    'day': row[7].strip(),
                    'number': row[0],
                    'week_type': week_type_text,
                    'title': row[1].strip(),
                    'classroom': row[2].strip(),
                    'lecturer': row[6].strip(),
                    'time_start': str(row[4])[:5],
                    'time_end': str(row[5])[:5]
                })
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('show_group_schedule: {}'.format(str(e)))
        finally:
            return render_template('show_group_schedule.html',
                                   title='Расписание занятий отдельной группы', form=form, schedule_table=schedule_table)

    return render_template('show_group_schedule.html',
                           title='Расписание занятий отдельной группы', form=form)


@bp.route('/show_group_exams', methods=['GET', 'POST'])
@login_required
def show_group_exams():
    form = ShowGroupDataForm()

    if form.validate_on_submit():
        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()

        exams_table = []
        try:
            with ScheduleDB(current_app.config) as db:
                db_data = db.get_group(organization, faculty, group)

                if db_data is None:
                    flash('Группы нет в базе данных')
                    return render_template('show_group_exams.html',
                                           title='Расписание экзаменов отдельной группы', form=form)

                tag = db_data[1]
                exams = db.get_exams(tag)

            for row in exams:
                exams_table.append({
                    'day': row[0],
                    'title': row[1].strip(),
                    'classroom': row[2].strip(),
                    'lecturer': row[3].strip()
                })
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('show_group_exams: {}'.format(str(e)))
        finally:
            return render_template('show_group_exams.html',
                                   title='Расписание экзаменов отдельной группы', form=form, exams_table=exams_table)

    return render_template('show_group_exams.html',
                           title='Расписание экзаменов отдельной группы', form=form)
