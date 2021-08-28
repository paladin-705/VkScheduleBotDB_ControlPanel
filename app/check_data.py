from flask import Blueprint, render_template, flash, current_app

from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename

from app.scheduledb import ScheduleDB
import json
import os

bp = Blueprint('check_data', __name__)


class CheckForm(FlaskForm):
    file = FileField('json файл с расписанием', validators=[DataRequired(), FileAllowed(['json'])])
    submit = SubmitField('Проверить файл', render_kw={"onclick": "show_loading_message()"})


@bp.route('/check_data', methods=['GET', 'POST'])
@login_required
def check_data():
    form = CheckForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        file_path = current_app.config['UPLOAD_DIR_PATH']
        form.file.data.save(file_path + filename)

        new_groups = []
        try:
            with open(file_path + filename) as json_file:
                json_data = json.load(json_file)

            for org in json_data:
                for faculty in json_data[org]:
                    for group in json_data[org][faculty]:
                        data_org = org.strip()
                        data_faculty = faculty.strip()
                        data_group = group.strip()

                        # Проверка наличия группы в базе
                        with ScheduleDB(current_app.config) as db:
                            db_data = db.get_group(data_org, data_faculty, data_group)

                            if db_data is None:
                                new_groups.append({
                                    'organization': data_org,
                                    'faculty': data_faculty,
                                    'group': data_group
                                })
            flash('JSON файл с расписанием успешно проверен')
        except BaseException as e:
            flash(str(e))
            current_app.logger.warning('check_data: {}'.format(str(e)))
        finally:
            os.remove(os.path.join(file_path, filename))
            return render_template('check_data.html', form=form, new_groups=new_groups)
    return render_template('check_data.html', form=form)