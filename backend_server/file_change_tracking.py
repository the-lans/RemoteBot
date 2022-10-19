import os
from os.path import getmtime, getsize, isdir, isfile, join
import tempfile
from pathlib import Path


class FileChangeTracking:
    def __init__(self, path=None, tmp_file=None, threshold1=0, threshold2=0):
        self.path = path
        self.size = 0
        self.dtm = 0.0
        self.pointer = 0
        if path:
            self.check()
        self.pointer = self.size
        self.tmp_file = self.get_tmp_file(tmp_file) if tmp_file else None
        self.threshold1 = threshold1
        self.threshold2 = threshold2 if threshold2 else threshold1

    @staticmethod
    def get_tmp_file(tmp_path):
        return join(tmp_path, Path(tempfile.NamedTemporaryFile().name).stem + '.txt') if isdir(tmp_path) else tmp_path

    def clear_tmp_file(self):
        if self.tmp_file and isfile(self.tmp_file):
            os.remove(self.tmp_file)

    def check(self):
        dtm = getmtime(self.path)
        if dtm > self.dtm:
            size = getsize(self.path)
            self.size, self.dtm = (size, dtm)
            if size < self.size:
                self.pointer = 0
        return self.size - self.pointer

    def read(self):
        with open(self.path, 'rt') as fp:
            fp.seek(self.pointer, 0)
            content = fp.read()
        self.pointer = self.size
        return content

    def divide_content(self, content, delta=None):
        if delta is None:
            delta = len(content)
        delta = len(content)
        if self.tmp_file and delta > self.threshold2:
            with open(self.tmp_file, 'wt') as fp:
                fp.write(content)
            return content[: self.threshold1], self.tmp_file
        else:
            return content, None

    def set_content(self, content):
        delta = len(content)
        if delta == 0:
            return '', None
        # self.write(content)
        return self.divide_content(content, delta)

    def get_content(self):
        delta = self.size - self.pointer
        if delta == 0:
            return '', None
        content = self.read()
        return self.divide_content(content, delta)
