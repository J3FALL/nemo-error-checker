import glob
import logging
import os

from src.experiment import Experiment


class BladeChecker:
    def __init__(self, date_from, date_to):
        self._storage_path = os.environ['STORAGE_PATH']
        self._date_from = date_from
        self._date_to = date_to
        self.init_logging()

    def init_logging(self):
        logging.basicConfig(filename='../logs/errors.log', level=logging.INFO)

    def check_local_storage(self):
        logging.info('Started')
        files = self.get_all_netcdf_files()
        print("files amount : %d" % len(files))
        exp = Experiment(date_from=self._date_from, date_to=self._date_to, resulted_files=[files])
        errors = exp.check_for_absence()
        logging.info('Finished')

        return errors

    def get_all_netcdf_files(self):
        files = []
        for file_name in glob.iglob(self._storage_path + "**/*.nc", recursive=True):
            files.append(self.path_leaf(file_name))
        return files

    def path_leaf(self, path):
        head, tail = os.path.split(path)
        return tail