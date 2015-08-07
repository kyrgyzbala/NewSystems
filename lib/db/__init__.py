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