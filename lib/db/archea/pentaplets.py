__author__ = 'Sanjarbek Hudaiberdiev'

import MySQLdb as mdb
connection = mdb.connect(host='mysql-dev', user='hudaiber', db='PatternQuest', passwd='buP!est9')



def setup_cursor():
    try:
        cursor = connection.cursor()
        return cursor
    except ConnectionDoesNotExist:
        print "Database not configured"
        return None


def get_multiple_kplets():

    _sql_cmd = """select  ap.id, count(*) cnt, group_concat(convert(apw.file_id, char(15))) as file_ids
                  from archea_5plets ap
                  inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
                  group by ap.id
                  having count(*)>1
                  order by cnt desc"""

    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd)

    return _cursor.fetchall()


def store_kplets(kplets, fname):

    for kplet in kplets:
        l = list(kplet)
        l.sort()
        kplet_id = retrieve_pentaplet_id(l)

        if not kplet_id:
            insert_pentaplet(l)
            kplet_id = retrieve_pentaplet_id(l)
        connection.commit()

        file_id = get_file_id(fname)
        insert_pentaplet_file(kplet_id, file_id)


def get_archaea_kplets():

    sql_cmd = """select apc.*, s1.cnt, s1.wgt
                 from (
                        select ap.id ,count(*) as cnt, sum(w.weight) as wgt
                        from archea_5plets ap
                        inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
                        inner join archea_win10_files awf on apw.file_id = awf.id
                        inner join sources s on awf.source_id=s.id
                        inner join weights w on w.genome_id=s.genome_id
                        group by ap.id ) s1
                 inner join archea_5plets_codes apc on s1.id=apc.id
                 order by s1.wgt desc"""

    cursor = setup_cursor()
    cursor.execute(sql_cmd)

    return cursor.fetchall()


def archea_kplet_ids2files(id_list):

    _sql_cmd = """select distinct awf.name
                  from archea_5plets ap
                  inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
                  inner join archea_win10_files awf on apw.file_id = awf.id
                  where ap.id in (%s)"""

    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd % " , ".join(id_list))
    return [l[0] for l in _cursor.fetchall()]


def insert_pentaplet_file(kplet_id, file_id):
    sql_cmd = """insert into archea_5plets_win10 values (%d, %d)"""
    sql_cmd = sql_cmd%(kplet_id, file_id)

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    connection.commit()


def retrieve_pentaplet_id(profiles):
    profile2id = map_profile2id(profiles)

    sql_cmd = """select id from archea_5plets where kplet_1=%d and kplet_2=%d and kplet_3=%d and kplet_4=%d and kplet_5=%d"""
    sql_cmd = sql_cmd % (profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()

    if rows:
        return rows[0][0]
    return None


def insert_pentaplet(profiles):
    profile2id = map_profile2id(profiles)

    sql_cmd = """insert into archea_5plets (kplet_1, kplet_2, kplet_3, kplet_4, kplet_5) values (%d, %d, %d, %d, %d)"""
    sql_cmd = sql_cmd%(profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)


def get_code_kplet(kplet_id):
    _sql_cmd = """select kplet_1, kplet_2, kplet_3, kplet_4, kplet_5 from archea_5plets_codes where id = %s""" % kplet_id
    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd)
    return _cursor.fetchall()[0]