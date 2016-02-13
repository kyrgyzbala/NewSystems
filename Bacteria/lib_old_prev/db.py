__author__ = 'Sanjarbek Hudaiberdiev'

import sys



def file_name2id():
    _cursor = setup_cursor()
    _sqlcmd = """ select id, name from  bacteria_win10_files"""

    _cursor.execute(_sqlcmd)
    print {v: int(k) for k, v in _cursor.fetchall()}


def map_profile2id(profile_list):

    sql_cmd = """select code, id from cdd_profiles where code in ('%s')"""
    sql_cmd %= "','".join(profile_list)
    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    return {row[0]: int(row[1]) for row in cursor.fetchall()}


def retrieve_pentaplet_id(profiles):
    profile2id = map_profile2id(profiles)

    sql_cmd = """select id from bacteria_5plets where kplet_1=%d and kplet_2=%d and kplet_3=%d and kplet_4=%d and kplet_5=%d"""
    sql_cmd = sql_cmd % (profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()

    if rows:
        return rows[0][0]
    return None


def insert_pentaplet(profiles):
    profile2id = map_profile2id(profiles)

    sql_cmd = """insert into bacteria_5plets (kplet_1, kplet_2, kplet_3, kplet_4, kplet_5) values (%d, %d, %d, %d, %d)"""
    sql_cmd = sql_cmd%(profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])

    cursor = setup_cursor()
    cursor.execute(sql_cmd)


def get_file_id(fname):
    sql_cmd = """select id from bacteria_win10_files where name='%s'"""
    sql_cmd %= fname
    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()
    assert len(rows) <= 1

    if not rows:
        raise Exception("File not found in database:%s" % fname)

    return rows[0][0]


def case_observed(kplet_id, file_id):

    sql_cmd = """select * from bacteria_5plets_win10 where kplet_id=%d and file_id=%d"""
    sql_cmd %= (kplet_id, file_id)

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()
    return True if rows else False


def insert_pentaplet_file(kplet_id, file_id):

    if not case_observed(kplet_id, file_id):
        sql_cmd = """insert into bacteria_5plets_win10 values (%d, %d)"""
        sql_cmd = sql_cmd%(kplet_id, file_id)

        cursor = setup_cursor()
        cursor.execute(sql_cmd)
        connection.commit()


def store_kplets(kplets, fname):

    sql_fmt = """"""

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


if __name__=='__main__':

    fname2id = file_name2id()
    print fname2id
