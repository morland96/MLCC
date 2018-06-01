from celery import Celery
from celery.signals import celeryd_after_setup, worker_shutdown
from celery.utils.log import get_task_logger
from mlcc.node.config import Config
from mlcc import util
from mlcc.model import Node, connect, Task
from shutil import copy, copytree, rmtree
from queue import Queue
import os
import psutil
import json
connect("mlcc", connect=False)  # Connect database
app = Celery('ampqp://guest:guest@localhost//')
# Load config
app.config_from_object(Config)
SERVERFILE_PATH = Config.file_server
LOCALFILE_PATH = Config.file_local
logger = get_task_logger(__name__)
DTYPE_FILE = 0b1
DTYPE_DATA = 0b10

worker_db_id = None
cpu_usage_history = Queue()
cpu_freq_history = Queue()

app.conf.beat_schedule = {
    'schedule-every-5-seconds': {
        'task': 'mlcc.node.worker.schedule',
        'schedule': 5.0
    }
}


@celeryd_after_setup.connect
def celeryd_after_setup(sender, **kwargs):
    node = Node()
    node.cpu_usage_history = []
    node.hostname = str(sender)
    node.save()
    global worker_db_id
    worker_db_id = str(node.id)
    logger.info("worker is ready with db id: " + worker_db_id)
    logger.info("kwargs: " + str(kwargs))


@worker_shutdown.connect
def worker_shutdown(sender, **kwargs):
    logger.info("Worker shutting down signal")
    logger.info(worker_db_id)
    node = Node.objects(id=worker_db_id)
    if len(node) > 0:
        node.delete()


@app.task()
def schedule():
    cpu_usage = psutil.cpu_percent()
    cpu_freq = psutil.cpu_freq()
    status = {'cpu_usage': cpu_usage, 'cpu_freq': cpu_freq}
    indent_status = json.dumps(status, indent=1)
    logger.info(f"scheduling: \n {indent_status}")

    node = Node.objects(id=worker_db_id)[0]
    node.cpu_usage = cpu_usage
    node.cpu_freq = cpu_freq[0]
    cpu_usage_history = node.cpu_usage_history
    cpu_usage_history.append(cpu_usage)
    if len(cpu_usage_history) > 3:
        node.cpu_usage_history = cpu_usage_history[1:]
    else:
        node.cpu_usage_history = cpu_usage_history
    node.save()
    logger.info(cpu_usage_history)


@app.task()
def new_task(uuid, language, data_num, input_list=None):
    """Recived a task and execute it.
        Task will firstly register current node as the cousumer node of this task in database. Then transfer all data set from server to local and start exectue. After all done, it will call the result task of server to acknowledge result data is ready.
    Args:
        uuid (str): task uuid
        language (str): language type
        data_num (int): total data_num
        input_list (list, optional): Defaults to None. input list
    """

    logger.info("\nRecived task: " + str({uuid, data_num}))
    tasks = Task.objects(id=uuid)
    node = Node.objects(id=worker_db_id)[0]
    task = tasks[0]
    task.consumer_node = node
    task.status = 1  # Set status to executing.
    task.save()
    transfer_files(uuid)
    local_file_path = LOCALFILE_PATH + '/tasks/' + uuid
    logger.info("\nStart execute")
    runtime_path = LOCALFILE_PATH + '/tmp/' + uuid
    result_path = LOCALFILE_PATH + '/result/' + uuid
    remove_if_exist(runtime_path)
    os.mkdir(runtime_path)
    os.mkdir(result_path)
    scripts_path = os.listdir(local_file_path)
    for path in scripts_path:
        if path == 'data':
            continue
        src_path = os.path.join(local_file_path, path)
        dst_path = os.path.join(runtime_path, path)
        try:
            logger.debug("Copy file: " + src_path + " --> " + dst_path)
            if os.path.isdir(src_path):
                copytree(src_path, dst_path)
            else:
                copy(src_path, dst_path)
        except OSError as err:
            raise err
    data_sets_path = os.path.join(local_file_path + '/data')
    data_sets = os.listdir(data_sets_path)
    assert (data_num == len(data_sets))
    progress = 1
    for data_set in data_sets:
        logger.info("Found data_set: " + data_set)
        logger.info("Copying files...")
        remove_if_exist(runtime_path + '/data')
        remove_if_exist(runtime_path + '/result')
        copytree(
            os.path.join(data_sets_path, data_set), runtime_path + '/data')
        os.mkdir(runtime_path + '/result')
        logger.info("Done")
        logger.info("Building Code runner...")
        core = build_core(language, data_set, runtime_path)
        core.execute()
        logger.info("Execute Done, collecting result")
        copytree(runtime_path + '/result', result_path + '/' + data_set)
        task.progress = progress
        progress = progress + 1
        task.save()
    transfer_result(uuid)
    task.status = 2
    task.save()
    app.send_task('mlcc.worker.result', args=[uuid])


def build_core(language, data_set, runtime_path) -> 'CodeCore':
    code = PythonCore()
    code.work_path = runtime_path
    code.read_script(runtime_path + '/main.py')
    code.fill_input({})
    return code


def remove_if_exist(path):
    if os.path.exists(path):
        rmtree(path)
        logger.info("Remove exist path: " + path)


def transfer_files(uuid):
    server_tar_path = SERVERFILE_PATH + 'tasks/' + uuid + '.tar.gz'
    local_file_path = LOCALFILE_PATH + '/tasks/' + uuid
    tar_path = local_file_path + '.tar.gz'
    copy(server_tar_path,
         tar_path)  # Copy without stats. Check copy2 if need stats
    util.un_targz(tar_path, local_file_path)
    logger.info("\nFile transfer to: " + local_file_path + "/ .....Done")
    return local_file_path


def transfer_result(uuid):
    result_path = LOCALFILE_PATH + '/result/' + uuid
    tar_path = result_path + '.tar.gz'
    util.targz(result_path + '/', tar_path)
    copy(tar_path, SERVERFILE_PATH + '/tasks_result/')


class CodeCore:
    base_path = LOCALFILE_PATH + '/tmp'

    def __init__(self):
        self._variable_dict = {}
        self.input_dict = None
        self.output_keys = []
        self.output_dict = None
        self.script = None
        self.language = "None"
        self.work_path = None

    def read_script(self, script_path: str):
        with open(script_path) as file:
            self.script = file.read()

    def fill_input(self, input_dict):
        self.input_dict = input_dict
        pass

    def get_output(self, keys=None):
        if keys is None:
            keys = self.output_keys
        output_dict = {}
        for key in keys:
            if key in self._variable_dict:
                output_dict[key] = self._variable_dict[key]
        return output_dict


class PythonCore(CodeCore):
    def __init__(self):
        super(PythonCore, self).__init__()
        self._global_dict = {}
        self.language = "Python"

    def execute(self):
        """PythonCore execute function. Execute and export result ot `output_dict` based on `output_keys`
        Raises:
            NoScriptException: Execute script not exist.
        """

        if self.script is not None:
            if self.input_dict is not None:
                self._variable_dict = {}
                self._variable_dict.update(self.input_dict)
                change_path_script = '''import os\nos.chdir('%s')''' % self.work_path
                exec(change_path_script)
                exec(self.script, self._global_dict, self._variable_dict)
                self.get_output()
            else:
                raise NoInputException("Input dict has not been filled")
        else:
            raise NoScriptException("None script has been loaded!")


def python_worker(script, param_dict):
    pass


"""Error Classes
"""


class NoScriptException(Exception):
    pass


class NoInputException(Exception):
    pass
