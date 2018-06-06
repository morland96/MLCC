from celery import Celery
from celery.utils.log import get_task_logger
from mlcc.config import Config
from mlcc.model import Task, Work, connect
import os
from mlcc.util import targz, un_targz
from shutil import copy, copytree
connect("mlcc", connect=False)
app = Celery('ampqp://guest:guest@localhost//')
app.config_from_object(Config)
SERVERFILE_PATH = Config.file_server
logger = get_task_logger(__name__)


@app.task
def result(task_uuid):
    """Collect result
    Args:
        task_uuid (str): Result's parent's uuid
    """
    task = Task.objects(id=task_uuid)[0]
    task.status = 3  # Set status as Done
    task.save()
    logger.info("\nCollecting result: " + task_uuid)
    un_targz(SERVERFILE_PATH + '/tasks_result/' + task_uuid + '.tar.gz',
             SERVERFILE_PATH + '/tasks_result/' + task_uuid)
    tasks = task.work.get_executing()
    if len(tasks) > 0:
        logger.info(f"Still {len(tasks)} running")
    else:
        logger.info("All is done, repack result.")
        tasks = task.work.tasks()
        work_id = str(task.work.id)
        os.mkdir(SERVERFILE_PATH + '/works_result/' + work_id)
        work_dir = SERVERFILE_PATH + '/works_result/' + work_id + '/'
        for task in tasks:
            task_id = str(task.id)
            task_dir = SERVERFILE_PATH + '/tasks_result/' + task_id + '/'
            data_set = os.listdir(task_dir)
            for data in data_set:
                copytree(task_dir + data, work_dir + data)
        task.work.done()
        logger.info("Work result is ready! ")
        targz(work_dir, work_dir + '../' + work_id + '.tar.gz')


def start_task(task_uuid, language):
    """Send a task to queue. Please make sure everyting is ready before send task.
    
    Args:
        uuid (str): uuid of task to send
    """
    logger.info("Send task: " + task_uuid)
    task = Task.objects(id=task_uuid)[0]
    task.status = 0
    task.save()
    data_num = wrap_task(task_uuid)
    app.send_task(
        'mlcc.node.worker.new_task', args=[task_uuid, language, data_num])


@app.task
def create_task(uuid, language, batch_size):
    """Split and start work with uuid
    Args:
        uuid (str): work's uuid
        language (str): code language
        batch_size (int): each batch's size for split
    """
    work_path = SERVERFILE_PATH + '/works/' + uuid
    # Register work in database.
    work = Work.objects(id=uuid)[0]
    work.start()
    copytree(SERVERFILE_PATH + '/upload/scripts/' + work.script_id, work_path)
    copytree(SERVERFILE_PATH + '/upload/datasets/' + work.dataset_id,
             work_path + '/data/')
    data_set = os.listdir(work_path + '/data')
    task_list = []
    batch_remain = 0
    logger.info("Spliting data set...")
    for data_name in data_set:
        if batch_remain == 0:  # Check if batch is full
            # Register a new task
            task = work.new_task()
            task_list.append(task)
            task_uuid = str(task.id)
            logger.debug("Start a new batch: " + task_uuid)
            logger.debug("Copying scripts")
            batch_remain = batch_size
            os.mkdir(SERVERFILE_PATH + '/tasks/' + task_uuid)
            copy_code(uuid, task_uuid)
        logger.debug("Transfer data: " + data_name)
        copytree(
            work_path + '/data/' + data_name,
            SERVERFILE_PATH + '/tasks/' + task_uuid + '/data/' + data_name)
        batch_remain = batch_remain - 1
    for task in task_list:
        task_uuid = str(task.id)
        logger.info("Found task: " + task_uuid)
        start_task(task_uuid, language)


def copy_code(work_id, task_id):
    """Copy files from works floder ato tasks folder except.
    Args:
        work_id (str): work's uuid
        task_id (str): task's uuid
    """

    work_path = SERVERFILE_PATH + '/works/' + work_id + '/'
    task_path = SERVERFILE_PATH + '/tasks/' + task_id + '/'
    scripts_path = os.listdir(work_path[:-1])
    for path in scripts_path:
        if path == 'data':
            continue
        src_path = os.path.join(work_path, path)
        dst_path = os.path.join(task_path, path)
        logger.debug("Copy file: " + src_path + " --> " + dst_path)
        if os.path.isdir(src_path):
            copytree(src_path, dst_path)
        else:
            copy(src_path, dst_path)


def wrap_task(uuid):
    targz(SERVERFILE_PATH + '/tasks/' + uuid + '/',
          SERVERFILE_PATH + '/tasks/' + uuid + '.tar.gz')
    logger.info("\Task has been wrapped")
    return len(os.listdir(SERVERFILE_PATH + '/tasks/' + uuid + '/data/'))


def create_dataset(uuid):
    un_targz(SERVERFILE_PATH + '/upload/datasets/' + uuid + '.tar.gz',
             SERVERFILE_PATH + '/upload/datasets/' + uuid + '/')
    logger.info(f"Get uploaded files{uuid}")


def create_script(uuid):
    un_targz(SERVERFILE_PATH + '/upload/scripts/' + uuid + '.tar.gz',
             SERVERFILE_PATH + '/upload/scripts/' + uuid + '/')
    logger.info(f"Get uploaded scripts{uuid}")
