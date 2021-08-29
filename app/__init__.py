from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

import os
from logging.config import dictConfig

from app.helpers import del_end_space
from app.scheduledb import ScheduleDB

bootstrap = Bootstrap()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.cfg'), silent=True)

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)-15s] [ %(levelname)s ] in %(module)s: %(message)s',
        }},
        'handlers': {'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': app.config['LOG_DIR_PATH'] + 'control_panel.log',
            'formatter': 'default',
            'maxBytes': 4096,
            'backupCount': 5
        }},
        'root': {
            'level': 'WARNING',
            'handlers': ['file']
        }
    })

    bootstrap.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к этой странице вам необходимо авторизоваться'
    login_manager.init_app(app)

    from app.main_data import bp as main_data_bp
    app.register_blueprint(main_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.show_data import bp as show_data_bp
    app.register_blueprint(show_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.parse_data import bp as parse_data_bp
    app.register_blueprint(parse_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.check_data import bp as check_data_bp
    app.register_blueprint(check_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.add_data import bp as add_data_bp
    app.register_blueprint(add_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.update_data import bp as update_data_bp
    app.register_blueprint(update_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.delete_data import bp as delete_data_bp
    app.register_blueprint(delete_data_bp, url_prefix=app.config['FLASK_ROUTE_PATH'])

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix=(app.config['FLASK_ROUTE_PATH'] + '/auth'))

    return app
