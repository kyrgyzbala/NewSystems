__author__ = 'hudaiber'

import sys
sys.path.append('../')
from .. import DbClass


def map_file_id2name():
    _db = DbClass()
    _db.cmd = """select id, name from archea_win10_files"""

    return {str(l[0]): l[1] for l in _db.retrieve()}


def map_name2file_id():
    _db = DbClass()
    _db.cmd = """select name, id from archea_win10_files"""

    return {str(l[0]): l[1] for l in _db.retrieve()}
