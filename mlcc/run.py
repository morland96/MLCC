from flask import Flask, request, jsonify, redirect
from flask_autoindex import AutoIndex
import json
import logging
import logging.handlers
import sys
import pymongo
from mlcc.model import User, connect, File, Script, Work, Node
import mlcc.worker as server_worker
from mlcc.flask_config import Config
import os
import shutil
from functools import wraps

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

__version__ = '1.0'

# logger
time_format = '%Y-%m-%dT%H:%M:%S.%f'
# Add StremHandler and FileHandler
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("mlcc.log")
file_handler.setFormatter(
    logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(stream_handler)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)
app.config.from_object(Config)
logger = app.logger

# Connect Database
client = pymongo.MongoClient()
db = client.mlcc
connect("mlcc")


def start_app():
    app.run(debug=True)


def auth(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = User.verify_auth_token(
            request.headers.get('Authentication-Token'))
        if user == -1:
            return jsonify({"error": "Not allowed"}), 401
        if user is None:
            return jsonify({}), 403
        print(user.username)
        return func(user, *args, **kwargs)

    return decorator


# auto_bp = Blueprint('auto_bp', __name__)
# AutoIndexBlueprint(auto_bp, browse_root='/var/mlcc/server')
# app.register_blueprint(auto_bp, url_prefix='/api/directory')
idx = AutoIndex(
    app,
    '/var/mlcc/server',
    add_url_rules=False,
    silk_options={'silk_path': '/directory/icons'})


@app.route('/directory/')
@app.route('/directory/<path:path>')
def autoindex(path='.'):
    return idx.render_autoindex(path)


"""
Basic route for redirect frontend page.
'catch_all' will return the SPA page who is build by npm based on npm.
"""

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     return render_template("index.html")


@app.route('/__webpack_hmr')
def npm():
    return redirect("http://localhost:8080/__webpack_hmr")


""" RESTful API :
Consider for compatibility and accessibility. We desgin all api path start from '/api' and use RESTful to make sure everything looks more resonable.
-----------------
Users API:
POST    /api/sessions       login and retrun a session

"""


@app.route('/api/sessions', methods=['POST'])
def login():
    data = request.get_data()
    logger.debug(data)
    try:
        data = json.loads(data)
    except Exception as e:
        return jsonify({}), 406
    username = data['username']
    password = data['password']
    logger.info("trying to log with username : " + username)
    user = User.login(username, password)
    if user is not None:
        return jsonify({"user": user.get_dict(), "token": user.token}), 201
    else:
        return jsonify({"id": 0}), 401


@app.route('/api/test/token', methods=['POST'])
@auth
def test_token(user):
    return jsonify({}), 403


@app.route('/api/user', methods=['GET'])
@auth
def get_user_info(user):
    if user == -1:
        return jsonify({'error': '未登录'}), 401
    if user is not None:
        return jsonify(user.get_dict()), 201
    else:
        return jsonify({}), 403


@app.route('/api/users', methods=['POST'])
def register_user():
    data = request.get_data()
    data = json.loads(data)
    username = data['username']
    password = data['password']
    privilege = data['privilege'] or 1
    users = User.objects(username=username, password=password)
    if len(users) > 0:
        return jsonify({'id': -1}), 409
    else:
        user = User()
        user.username = username
        user.password = password
        user.privilege = privilege
        user.save()
        return jsonify(user.get_dict()), 201


@app.route('/api/users/<string:username>', methods=['PUT'])
@auth
def update_user(user, username):
    if user.username == username:
        new_user = json.loads(request.get_data())
        user.update_with_dict(new_user)
        return jsonify(user.get_dict()), 201
    else:
        return 403


@app.route('/api/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    user = User.objects(username=username)
    if len(user) == 0:
        return jsonify({'status': -1}), 404
    user.delete()
    return jsonify({'status': 0}), 204


@app.route('/api/upload', methods=['POST'])
def upload_datasets():
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({}), 500

        f = File()
        f.save()
        file.save(
            os.path.join(app.config['UPLOAD_FOLDER'] + '/datasets/',
                         str(f.id) + '.tar.gz'))
        return jsonify({"uuid": str(f.id)}), 201
    return ""


@app.route('/api/datasets', methods=['POST'])
@auth
def create_datasets(user):
    data = json.loads(request.get_data())
    f = File.objects(id=data['uuid'])[0]
    f.uploader = user
    f.details = data['details']
    f.filename = data['filename']
    f.save()
    server_worker.create_dataset(data['uuid'])
    return jsonify(), 201


@app.route('/api/datasets', methods=['GET'])
@auth
def get_datasets(user):
    files = File.objects(uploader=user)
    files_list = []
    for f in files:
        files_list.append(f.get_dict())

    return jsonify(files_list), 200


@app.route('/api/datasets/<string:uuid>', methods=['DELETE'])
@auth
def delete_datasets(user, uuid):
    files = File.objects(id=uuid)
    if files is None:
        return jsonify(), 404
    files[0].delete()
    filepath = app.config['UPLOAD_FOLDER'] + '/datasets/' + uuid
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
    if os.path.exists(filepath + '.tar.gz'):
        os.remove(filepath + '.tar.gz')
    return jsonify(), 204


@app.route('/api/upload_script', methods=['POST'])
def upload_script():
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({}), 500
        s = Script()
        s.save()
        file.save(
            os.path.join(app.config['UPLOAD_FOLDER'] + '/scripts/',
                         str(s.id) + '.tar.gz'))
        return jsonify({"uuid": str(s.id)}), 201
    return ""


@app.route('/api/script', methods=['POST'])
@auth
def create_script(user):
    data = json.loads(request.get_data())
    s = Script.objects(id=data['uuid'])[0]
    s.uploader = user
    s.details = data['details']
    s.script_name = data['script_name']
    s.language = data['language']
    s.save()
    server_worker.create_script(data['uuid'])
    return jsonify(), 201


@app.route('/api/scripts', methods=['GET'])
@auth
def get_scripts(user):
    scripts = Script.objects(uploader=user)
    scripts_list = []
    for s in scripts:
        scripts_list.append(s.get_dict())

    return jsonify(scripts_list), 200


@app.route('/api/scripts/<string:uuid>', methods=['DELETE'])
@auth
def delete_scripts(user, uuid):
    scripts = Script.objects(id=uuid)
    if scripts is None:
        return jsonify(), 404
    scripts[0].delete()
    filepath = app.config['UPLOAD_FOLDER'] + '/scritps/' + uuid
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
    if os.path.exists(filepath + '.tar.gz'):
        os.remove(filepath + '.tar.gz')
    return jsonify(), 204


@app.route('/api/scripts/<string:uuid>/main', methods=['GET'])
def get_script_main(uuid):
    scripts = Script.objects(id=uuid)
    if scripts is None:
        return jsonify(), 404
    with open(app.config['UPLOAD_FOLDER'] + '/scripts/' + uuid + '/main.py'
              ) as f:
        content = f.read()
        return jsonify({"content": content}), 200


@app.route('/api/works', methods=['GET'])
def get_works():
    works = Work.objects()
    work_list = []
    for work in works:
        work_list.append(work.get_dict())
    return jsonify(work_list), 200


@app.route('/api/works', methods=['POST'])
@auth
def create_work(user):
    data = json.loads(request.get_data())
    work = Work()
    work.batch_size = data['batch_size']
    work.work_name = data['work_name']
    work.details = data['details']
    work.dataset_id = data['dataset_id']
    work.script_id = data['script_id']
    work.user = user
    work.data_num = len(
        os.listdir(
            app.config['UPLOAD_FOLDER'] + '/datasets/' + work.dataset_id))
    work.save()
    server_worker.create_task.delay(str(work.id), "python", work.batch_size)
    return jsonify({"uuid": str(work.id)})


"""Monitoring API desgined for worker schedule
"""


@app.route('/api/nodes/status', methods=['GET'])
@auth
def get_nodes_status(user):
    nodes = Node.objects()
    status = []
    for node in nodes:
        status.append(node.get_dict())
    return jsonify(status), 200