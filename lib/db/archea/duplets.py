__author__ = 'Sanjarbek Hudaiberdiev'

import MySQLdb as mdb
connection = mdb.connect(host='mysql-dev', user='hudaiber', db='PatternQuest', passwd='buP!est9')
import db_tools as t


def setup_cursor():
    try:
        cursor = connection.cursor()
        return cursor
    except ConnectionDoesNotExist:
        print "Database not configured"
        return None


def store_kplets(kplets, fname):

    for kplet in kplets:
        l = list(kplet)
        l.sort()
        kplet_id = get_kplet_id(l)

        if not kplet_id:
            insert_kplet(l)
            kplet_id = get_kplet_id(l)
        connection.commit()

        file_id = t.get_file_id(fname)
        insert_kplet_file(kplet_id, file_id)


def insert_kplet_file(kplet_id, file_id):
    sql_cmd = """insert ignore into archea_2plets_win10 values (%d, %d)"""
    sql_cmd = sql_cmd % (kplet_id, file_id)

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    connection.commit()


def get_kplet_id(profiles):
    profile2id = t.map_profile2id(profiles)

    sql_cmd = """select id from archea_2plets where kplet_1=%d and kplet_2=%d"""
    sql_cmd = sql_cmd % (profile2id[profiles[0]], profile2id[profiles[1]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()

    if rows:
        return rows[0][0]
    return None


def insert_kplet(profiles):
    profile2id = t.map_profile2id(profiles)

    sql_cmd = """insert into archea_2plets (kplet_1, kplet_2) values (%d, %d)"""
    sql_cmd = sql_cmd % (profile2id[profiles[0]], profile2id[profiles[1]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)


def get_code_kplet(kplet_id):
    _sql_cmd = """SELECT cp1.code, cp2.code
                    FROM PatternQuest.archea_2plets ap
                    inner join cdd_profiles cp1 on cp1.id = ap.kplet_1
                    inner join cdd_profiles cp2 on cp2.id = ap.kplet_2
                    where ap.id = %d""" % kplet_id
    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd)
    return _cursor.fetchall()[0]


def get_multiple_kplets():

    _sql_cmd = """select  ap.id, count(*) cnt, group_concat(convert(apw.file_id, char(15))) as file_ids
                  from archea_2plets ap
                  inner join archea_2plets_win10 apw on ap.id = apw.kplet_id
                  group by ap.id
                  having count(*)>1
                  order by cnt desc"""

    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd)

    return _cursor.fetchall()