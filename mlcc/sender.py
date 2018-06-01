from mlcc.config import Config
from mlcc.model.Node import Node
from mlcc.util import targz
import mlcc.worker as server_worker
import mlcc.node.worker as node_worker
from mongoengine import connect
from uuid import uuid1
import os
from shutil import copy, copytree
import logging

SERVERFILE_PATH = Config.file_server
logger = logging.getLogger()


def create_task(task_uuid, language):
    logger.info("Send task: " + task_uuid)
    send_task(task_uuid, language)


def send_task(uuid, language):
    """Send a task to queue. Please make sure everyting is ready before send task.
    
    Args:
        uuid (str): uuid of task to send
    """
    data_num = wrap_task(uuid)
    node_worker.new_task.delay(uuid, language, data_num, node_worker.DTYPE_FILE)


def start_work(uuid, language, batch_size):
    """Split and start work with uuid
    Args:
        uuid (str): work's uuid
        language (str): code language
        batch_size (int): each batch's size for split
    """
    work_path = SERVERFILE_PATH + '/works/' + uuid
    data_set = os.listdir(work_path + '/data')
    task_list = []
    batch_remain = 0
    logger.info("Spliting data set...")
    task_uuid = ""
    for data_name in data_set:
        if batch_remain == 0:  # Check if batch is full
            task_list.append(str(uuid1()))
            task_uuid = task_list[-1]
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
        logger.info("Found task: " + task)
        create_task(task, language)


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
