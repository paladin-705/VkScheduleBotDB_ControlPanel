# VkScheduleBot Control Panel
Панель управления базой данных бота. Предоставляет веб-интерфейс для взаимодействия с БД расписания, а также позволяет редактировать пользователей API бота (модуль [api_server](https://github.com/paladin-705/VkScheduleBot/tree/main/api_server)). Панель управления является модулем для [VkScheduleBot](https://github.com/paladin-705/VkScheduleBot).

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/paladin705/vk_schedule_bot_db_control_panel)

Docker Hub: [paladin705/vk_schedule_bot_db_control_panel](https://hub.docker.com/r/paladin705/vk_schedule_bot_db_control_panel)

## Зависимости
Модуль использует СУБД PostgreSQL для хранения данных. Адрес: `http://<адрес сервера><FLASK_ROUTE_PATH>`, где `<FLASK_ROUTE_PATH>` - переменная определяющая адрес сервера панели управления.

Сервер реализованный в docker контейнере не имеет прямого доступа к сети и использует сокет `/control_panel/socket/control_panel.sock` для обработки запросов. Чтобы передать поступающие запросы серверу, можно использовать nginx reverse proxy для передачи их на сокет сервера.

## Docker
Для запуска docker контейнера загружаемого с [Docker Hub](https://hub.docker.com/r/paladin705/vk_schedule_bot_db_control_panel) можно использовать следующую команду:
```shell
docker run \
    -v ./vk_bot_api/socket:/api/socket \
    -v ./vk_bot_api/log:/api/log \
    -e DB_NAME=<Введите значение параметра> \
    -e DB_USER=Введите значение параметра<> \
    -e DB_PASSWORD=<Введите значение параметра> \
    -e DB_HOST=<Введите значение параметра> \
    -e FLASK_ROUTE_PATH=<Введите значение параметра> \
    -e TZ=<Введите значение параметра> \
    paladin705/vk_schedule_bot_db_control_panel:latest
```

### Файлы
* `/control_panel/socket` - В данной директории находится сокет сервера: `control_panel.sock`. Он используется для обработки запросов к серверу
* `/control_panel/log` - Директория где располагаются логи сервера

### Переменные среды

* `DB_NAME` - Название базы данных (БД) PostgreSQL
* `DB_USER` - Имя пользователя БД
* `DB_PASSWORD` - Пароль пользователя БД
* `DB_HOST` - Адрес БД
* `FLASK_ROUTE_PATH` - Опредлеляет адрес сервера панели управления. Необязательный параметр. По умолчанию `/control_panel/`
* `TZ` - Часовой пояс. По умолчанию `Europe/Moscow`

## Создание пользователя API
Для работы с панелью управления вам необходим аккаунт пользователя, который также может использоваться для запросов к API в модуле [api_server](https://github.com/paladin-705/VkScheduleBot/tree/main/api_server).

Изначально в базе данных нет аккаунтов пользователей, поэтому если если вы ранее не создавали пользователей API (для модуля [api_server](https://github.com/paladin-705/VkScheduleBot/tree/main/api_server)), то вам необходимо создать имя пользователя и пароль, а затем сгенерировать bcrypt хеш пароля. Затем вам необходимо сохранить выбранное имя пользователя API и сгенерированный хеш пароля в таблицу `api_users` базы данных.

Если вы ранее создавали пользователей для модуля [api_server](https://github.com/paladin-705/VkScheduleBot/tree/main/api_server), то для взаимодействия с панелью управления вы можете использовать его данные.

Следующий пример показывает простой Python скрипт для создания нового пользователя API и панели управлени. Для его работы понадобятся библиотеки `bcrypt` и `psycopg2`:
```shell
pip install bcrypt psycopg2
```

После установки библиотек bcrypt и psycopg2, необходимо создать и запустить следующий скрипт для Python 3:
```python
import bcrypt
import psycopg2

# Данные нового пользователя панели управления
api_username = 'Имя пользователя панели управления'
api_password = 'Пароль пользователя панели управления'

# Параметры подключения к базе данных
db_name = 'Название базы данных (БД) PostgreSQL'
db_user = 'Имя пользователя БД'
db_password = 'Пароль пользователя БД'
db_host = 'Адрес сервера БД'
db_port = Порт сервера БД (число)

# Создание хеша пароля
pw_hash = bcrypt.hashpw(api_password.encode('utf-8'), bcrypt.gensalt())

# Загрузка нового пользователя панели управления в базу данных
con = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port)

cur = con.cursor()
cur.execute('INSERT INTO api_users(username, pw_hash) VALUES(%s,%s);', (api_username, pw_hash.decode('utf-8')))
con.commit()
```
Вам необходимо записать в переменные `api_username` и `api_password` желаемое имя пользователя и его пароль соответственно. Переменные `db_name`, `db_user`, `db_password`, `db_host` и `db_port` используются для установки соединения с сервером PostgreSQL базы данных. Вы должны использовать для их заполнения теже значения, что и для сервера панели управления (если скрипт запускается не с компьютера, на котором запущен сервер панели управления, то значение `db_host` и `db_port` может отличаться).

В дальнейшем вы сможете добавлять новых пользователей через веб-интерфейс панели управления.
