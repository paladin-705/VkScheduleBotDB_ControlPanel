from flask import current_app as app
import psycopg2


class ApiSettingsDB:
    def __init__(self, config):
        self.con = psycopg2.connect(
            dbname=config["API_DB_NAME"],
            user=config["API_DB_USER"],
            password=config["API_DB_PASSWORD"],
            host=config["API_DB_HOST"])
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.commit()
        self.con.close()

    def add_user(self, username, pw_hash):
        try:
            self.cur.execute('INSERT INTO api_users(username, pw_hash) VALUES(%s,%s);',
                             (username, pw_hash))
            self.con.commit()
            return True
        except BaseException as e:
            app.logger.warning('Add user failed. Error: {0}. Data: username={1}'.format(
                str(e), username))
            return False

    def delete_user(self, user_id):
        try:
            self.cur.execute('DELETE FROM api_users WHERE id = (%s);', (user_id, ))
            self.con.commit()
            return True
        except BaseException as e:
            app.logger.warning('Delete user failed. Error: {0}. Data: id={1}'.format(
                str(e), user_id))
            return False

    def get_user_info(self, username):
        data = None
        try:
            self.cur.execute("SELECT id, username, pw_hash FROM api_users WHERE username = (%s);", (username, ))
            data = self.cur.fetchone()
        except BaseException as e:
            app.logger.warning('Select user failed. Error: {0}. Data: username={1}'.format(str(e), username))
            raise e
        finally:
            return data

    def get_user_by_id(self, user_id):
        data = None
        try:
            self.cur.execute("SELECT id, username, pw_hash FROM api_users WHERE id = (%s);", (user_id, ))
            data = self.cur.fetchone()
        except BaseException as e:
            app.logger.warning('Select user failed. Error: {0}. Data: id={1}'.format(str(e), user_id))
            raise e
        finally:
            return data

    def get_users(self):
        data = None
        try:
            self.cur.execute("SELECT id, username FROM api_users;")
            data = self.cur.fetchall()
        except BaseException as e:
            app.logger.warning('Select users failed. Error: {0}'.format(str(e)))
            raise e
        finally:
            return data
