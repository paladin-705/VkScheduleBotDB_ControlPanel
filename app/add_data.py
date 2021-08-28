from flask import Blueprint, render_template, flash, current_app

from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename

from app.scheduledb import ScheduleDB
import json
import os

bp = Blueprint('add_data', __name__)


class UploadForm(FlaskForm):
    choices = [
        ('schedule', 'Расписание занятий'),
        ('exams', 'Расписание экзаменов')
    ]

    schedule_type = SelectField('Тип расписания', choices=choices, validators=[DataRequired()])
    file = FileField('json файл с расписанием', validators=[DataRequired(), FileAllowed(['json'])])
    submit = SubmitField('Добавить расписание')


class AddGroupForm(FlaskForm):
    organization = StringField('Название организации', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Название факультета', validators=[DataRequired(), Length(max=80)])
    group = StringField('Название группы', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Добавить группу')


def add_schedule(tag, schedule):
    failed_data_len = 0
    with ScheduleDB(current_app.config) as db:
        for lecture in schedule:
            day = lecture.get('day', None)
            number = lecture.get('number', None)
            week_type_text = lecture.get('week_type', None)
            title = lecture.get('title', None)

            if week_type_text == 'odd':
                week_type = 0
            elif week_type_text == 'even':
                week_type = 1
            elif week_type_text == 'all':
                week_type = 2
            else:
                week_type = None

            # Необязательные параметры
            classroom = lecture.get('classroom', None)
            time_start = lecture.get('time_start', None)
            time_end = lecture.get('time_end', None)
            lecturer = lecture.get('lecturer', None)

            if day is None or number is None or week_type is None or title is None:
                failed_data_len += 1
                continue
            else:
                if not db.add_lesson(tag, day, number, week_type,
                                     time_start, time_end, title, classroom, lecturer):
                    failed_data_len += 1
    return failed_data_len


def add_exams(tag, schedule):
    failed_data_len = 0
    with ScheduleDB(current_app.config) as db:
        for exam in schedule:
            # Обязательные параметры запроса
            day = exam.get('day', None)
            title = exam.get('title', None)

            # Необязательные параметры
            classroom = exam.get('classroom', None)
            lecturer = exam.get('lecturer', None)

            if day is None or title is None:
                failed_data_len += 1
                continue
            else:
                if not db.add_exam(tag, title, classroom, lecturer, day):
                    failed_data_len += 1
    return failed_data_len


@bp.route('/add_schedule_data', methods=['GET', 'POST'])
@login_required
def add_schedule_data():
    form = UploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        file_path = current_app.config['UPLOAD_DIR_PATH']
        form.file.data.save(file_path + filename)

        new_groups = []
        try:
            with open(file_path + filename) as json_file:
                json_data = json.load(json_file)

            failed_data_len = 0
            for org in json_data:
                for faculty in json_data[org]:
                    for group in json_data[org][faculty]:
                        data_org = org.strip()
                        data_faculty = faculty.strip()
                        data_group = group.strip()

                        # Проверка наличия группы в базе
                        with ScheduleDB(current_app.config) as db:
                            db_data = db.get_group(data_org, data_faculty, data_group)

                            if db_data is not None:
                                tag = db_data[1]
                            else:
                                tag = db.add_organization(data_org, data_faculty, data_group)
                                new_groups.append({
                                    'organization': data_org,
                                    'faculty': data_faculty,
                                    'group': data_group,
                                    'tag': tag
                                })

                        schedule = json_data[org][faculty][group]
                        if form.schedule_type.data == 'schedule':
                            failed_data_len += add_schedule(tag, schedule)
                        elif form.schedule_type.data == 'exams':
                            failed_data_len += add_exams(tag, schedule)
                        else:
                            failed_data_len += len(schedule)
            if not failed_data_len:
                flash('Расписание успешно загружено')
            else:
                flash('Часть занятий ({}) не удалось добавить'.format(failed_data_len))
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('add_schedule_data: {}'.format(str(e)))
        finally:
            os.remove(os.path.join(file_path, filename))
            return render_template('add_schedule_data.html', form=form, new_groups=new_groups)
    return render_template('add_schedule_data.html', form=form)


@bp.route('/add_group_data', methods=['GET', 'POST'])
@login_required
def add_group_data():
    form = AddGroupForm()

    if form.validate_on_submit():
        organization = form.organization.data.strip()
        faculty = form.faculty.data.strip()
        group = form.group.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                db_data = db.get_group(organization, faculty, group)

                if db_data is not None:
                    flash('Такая группа уже есть в базе данных')
                else:
                    tag = db.add_organization(organization, faculty, group)
                    flash('Группа успешно добавлена. Tag: {}'.format(tag))
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('add_group_data: {}'.format(str(e)))
        finally:
            return render_template('add_group.html', form=form)
    return render_template('add_group_data.html', form=form)
