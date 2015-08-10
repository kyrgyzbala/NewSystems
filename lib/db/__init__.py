__author__ = 'hudaiber'

import MySQLdb as mdb
connection = mdb.connect(host='mysql-dev', user='hudaiber', db='PatternQuest', passwd='buP!est9')


def setup_cursor():
    try:
        cursor = connection.cursor()
        return cursor
    except ConnectionDoesNotExist:
        print "Database not configured"
        return None


class DbClass(object):
    def __init__(self, cmd=None):
        self.cursor = setup_cursor()
        self.cmd = cmd

    def execute(self):
        self.cursor.execute(self.cmd)

    @staticmethod
    def commit():
        connection.commit()

    def retrieve(self):

        if not self.cmd:
            raise ValueError("Provide valid SQL command")

        self.execute()
        return self.cursor.fetchall()


def map_cdd2id():

    _db = DbClass()
    _db.cmd = """select code, id from cdd_profiles"""

    rows = _db.retrieve()

    return {row[0]: int(row[1]) for row in rows}


def map_id2cdd():
    _db = DbClass()
    _db.cmd = """select code, id from cdd_profiles"""

    rows = _db.retrieve()

    return {row[0]: int(row[1]) for row in rows}


def map_id2cdd_cdd2id_cdd2def():
    _db = DbClass()
    _db.cmd = """select code, id, description from cdd_profiles"""

    rows = _db.retrieve()

    _cdd2id, _id2cdd, _cdd2def = {}, {}, {}

    for row in rows:
        (code, id, desctiption) = row

        _cdd2id[code] = id
        _id2cdd[id] = code
        _cdd2def[code] = desctiption

    return _id2cdd, _cdd2id, _cdd2def

