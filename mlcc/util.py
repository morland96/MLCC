import os
import tarfile


def targz(source_dir, target_filename):
    with tarfile.open(target_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def un_targz(source_filename, target_dir):
    with tarfile.open(source_filename, "r:gz") as tar:
        tar.extractall(target_dir)