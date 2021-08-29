from flask import Blueprint, render_template, flash, current_app

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from app.scheduledb import ScheduleDB
import re

bp = Blueprint('update_data', __name__)


class UpdateGroupForm(FlaskForm):
    old_organization = StringField('Текущая организация', validators=[DataRequired(), Length(max=80)])
    old_faculty = StringField('Текущий факультет', validators=[DataRequired(), Length(max=80)])
    old_group = StringField('Текущая группа', validators=[DataRequired(), Length(max=50)])

    new_organization = StringField('Новая организация', validators=[DataRequired(), Length(max=80)])
    new_faculty = StringField('Новый факультет', validators=[DataRequired(), Length(max=80)])
    new_group = StringField('Новая группа', validators=[DataRequired(), Length(max=50)])

    submit = SubmitField('Изменить группу')


class UpdateGroupsNumberForm(FlaskForm):
    confirm_update = BooleanField('Подтверждение изменений', default=False, validators=[DataRequired()])
    submit = SubmitField('Изменить номера групп')


@bp.route('/update_data')
def update_data():
    return render_template('update_data.html', title='Изменение')


@bp.route('/update_group', methods=['GET', 'POST'])
def update_group():
    form = UpdateGroupForm()

    if form.validate_on_submit():
        old_organization = form.old_organization.data.strip()
        old_faculty = form.old_faculty.data.strip()
        old_group = form.old_group.data.strip()

        new_organization = form.new_organization.data.strip()
        new_faculty = form.new_faculty.data.strip()
        new_group = form.new_group.data.strip()
        try:
            with ScheduleDB(current_app.config) as db:
                old_data = db.get_group(old_organization, old_faculty, old_group)

                if old_data is not None:
                    old_tag = old_data[1]

                    new_data = db.get_group(new_organization, new_faculty, new_group)

                    if new_data is not None:
                        flash('Новые данные: Такая группа уже есть в базе данных')
                    else:
                        new_tag = db.update_organization(new_organization, new_faculty, new_group, old_tag)

                        if new_tag is not None:
                            flash('Группа успешно изменена. Tag: {}'.format(new_tag))
                        else:
                            flash('Ошибка изменения данных группы')
                else:
                    flash('Текущие данные: Такой группы нет в базе данных')
        except BaseException as e:
            flash(str(e))
        finally:
            return render_template('update_group.html', title='Изменение данных группы', form=form)
    return render_template('update_group.html', title='Изменение данных группы', form=form)


def inc_group_info(faculty_title, group_title):
    group_data = group_title.split('-')
    faculty_data = faculty_title.split(' ')

    changed = False

    new_group_title = group_title
    new_faculty_title = faculty_title

    if len(group_data) == 2:
        result = re.match(r'(\d{1,3})(\w*)', group_data[1])

        if result:
            items = result.groups()

            if len(items) == 2 \
                    and items[0].isdigit() \
                    and 2 <= len(items[0]) <= 3 \
                    and re.fullmatch(r'(\w+ )*\d \w+', faculty_title) is not None:

                changed = True

                if len(items[0]) == 2:
                    next_semester_number = int(items[0][0]) + 1
                    group_number = items[0][1]
                elif len(items[0]) == 3:
                    next_semester_number = int(items[0][:2]) + 1
                    group_number = items[0][2]
                else:
                    next_semester_number = 'SN'
                    group_number = 'G'

                new_group_title = '{}-{}{}{}'.format(group_data[0], next_semester_number, group_number, items[1])

                if len(faculty_data) == 2:
                    new_faculty_number = int(faculty_data[0])
                elif len(faculty_data) == 3:
                    new_faculty_number = int(faculty_data[1])
                else:
                    new_faculty_number = 0

                if next_semester_number % 2 != 0:
                    new_faculty_number += 1

                if len(faculty_data) == 2:
                    new_faculty_title = '{} {}'.format(new_faculty_number, faculty_data[1])
                elif len(faculty_data) == 3:
                    new_faculty_title = '{} {} {}'.format(faculty_data[0], new_faculty_number, faculty_data[2])
    return new_faculty_title, new_group_title, changed


@bp.route('/update_groups_number', methods=['GET', 'POST'])
def update_groups_number():
    form = UpdateGroupsNumberForm()

    if form.validate_on_submit():
        if not form.confirm_update.data:
            flash('Вы не подтвердили изменения ')
            return render_template('update_groups_number.html',
                                   title='Автоматическое изменение номеров групп', form=form)

        updated_groups_table = []
        error_groups_table = []
        skipped_groups_table = []

        try:
            with ScheduleDB(current_app.config) as db:
                org_data_list = db.get_organizations()
                for db_org_data in org_data_list:
                    org = db_org_data[0]

                    faculty_data_list = sorted(db.get_faculty(org), key=lambda x: x[0], reverse=True)
                    for db_faculty_data in faculty_data_list:
                        faculty = db_faculty_data[0]

                        groups_data_list = db.get_group_list(org, faculty)
                        for db_group_data in groups_data_list:
                            group, tag = db_group_data

                            new_faculty, new_group, group_changed = inc_group_info(faculty, group)

                            if group_changed:
                                new_tag = db.update_organization(org, new_faculty, new_group, tag)

                                if new_tag is not None:
                                    updated_groups_table.append({
                                        'organization': org,
                                        'old_faculty': faculty,
                                        'old_group': group,
                                        'old_tag': tag,
                                        'new_faculty': new_faculty,
                                        'new_group': new_group,
                                        'new_tag': new_tag
                                    })
                                else:
                                    error_groups_table.append({
                                        'organization': org,
                                        'faculty': faculty,
                                        'group': group,
                                        'tag': tag
                                    })
                            else:
                                skipped_groups_table.append({
                                    'organization': org,
                                    'faculty': faculty,
                                    'group': group,
                                    'tag': tag
                                })
            flash('Номера групп успешно изменены')
        except BaseException as e:
            flash(str(e))
        finally:
            return render_template('update_groups_number.html', title='Автоматическое изменение номеров групп',
                                   form=form, updated_groups_table=updated_groups_table,
                                   error_groups_table=error_groups_table, skipped_groups_table=skipped_groups_table)
    return render_template('update_groups_number.html', title='Автоматическое изменение номеров групп', form=form)
