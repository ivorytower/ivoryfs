#!/usr/bin/env python

import os
import sys

for p in ("../lib",
          "../lib/fusepy"):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), p))

import fuse
from fuse import FUSE, FuseOSError

class IvoryFs(fuse.Operations):
    def __init__(self, mirrored_dir):
        self.__mirrored_dir = mirrored_dir

    def __call__(self, op, path, *args):
        print("called " + op)
        return super(self.__class__, self).__call__(op, self.__mirrored_dir + path, *args)

    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    def getattr(self, path, fh = None):
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in ("st_atime", "st_ctime", "st_gid", "st_mode", "st_mtime",
            "st_nlink", "st_size", "st_uid"))

    open = os.open

    def read(self, path, size, offset, fh):
        file_size = os.stat(path).st_size
        offset = file_size - (offset + size)
        if offset < 0:
            size += offset
            offset = 0
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, size)[::-1]

    def readdir(self, path, fh):
        return [".", ".."] + os.listdir(path)

    def release(self, path, fh):
        return os.close(fh)

if __name__ == "__main__":
    fuse = FUSE(IvoryFs(sys.argv[2]), sys.argv[1], foreground = True, ro = True)
