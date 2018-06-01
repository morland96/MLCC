import unittest
import logging
import mlcc.node.worker as node_worker
import mlcc.worker as server_worker
from mlcc.model import Task, Work, connect
from shutil import copytree
logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s [%(levelname)s] %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
logger = logging.getLogger("test_worker")
server_worker.logger = logger
node_worker.logger = logger

connect("mlcc")


class TestWorker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_setp1_works(self):
        w = Work()
        w.save()
        uuid = str(w.id)
        copytree(server_worker.SERVERFILE_PATH + '/works/' + '1',
                 server_worker.SERVERFILE_PATH + '/works/' + uuid)
        server_worker.create_task(uuid, "Python", 2)

    def test_step2_task(self):
        t = Task()
        t.save()
        self.assertIsNotNone(t.id)
        logger.info(t.id)

    def test_step3_work(self):
        w = Work()
        w.save()
        task = w.new_task()
        task_id = task.id
        self.assertIsNotNone(task_id)
        self.assertEqual(task.work, w)
        w = Work.objects(id=str(task.work.id))
        self.assertEqual(len(w), 1)


if __name__ == "__main__":
    TestWorker.run()
