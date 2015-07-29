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


def file_name2id():
    _cursor = setup_cursor()
    _sqlcmd = """ select id, name
                  from  archea_win10_files"""

    _cursor.execute(_sqlcmd)
    print { v:int(k) for k,v in _cursor.fetchall()}


def map_profile2id(profile_list):

    sql_cmd = """select code, id from cdd_profiles where code in ('%s')"""
    sql_cmd = sql_cmd%"','".join(profile_list)
    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    return {row[0]: int(row[1]) for row in cursor.fetchall()}


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


def get_file_id(fname):
    sql_cmd = """select id from archea_win10_files where name='%s'"""
    sql_cmd = sql_cmd%fname
    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    rows = cursor.fetchall()
    assert len(rows) <= 1

    if not rows:
        raise Exception("File not found in database:%s" % fname)

    return rows[0][0]


def insert_pentaplet_file(kplet_id, file_id):
    sql_cmd = """insert into archea_5plets_win10 values (%d, %d)"""
    sql_cmd = sql_cmd%(kplet_id, file_id)

    cursor = setup_cursor()
    cursor.execute(sql_cmd)
    connection.commit()


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


def archea_files2src_org_map(files):

    _sql_cmd = """select awf.name, s.name, g.name
                  from archea_win10_files awf
                  inner join sources s on awf.source_id=s.id
                  inner join genomes g on s.genome_id = g.id
                  where awf.name in ('%s')"""

    _sql_cmd = _sql_cmd % "','".join(files)

    _cursor = setup_cursor()
    _cursor.execute(_sql_cmd)
    _org2src = {}
    _src2files = {}

    for row in _cursor.fetchall():
        parts = row
        [_file, _src, _org] = parts
        if _org in _org2src:
            _org2src[_org].update([_src])
        else:
            _org2src[_org] = set([_src])

        if _src in _src2files:
            _src2files[_src].update([_file])
        else:
            _src2files[_src] = set([_file])

    return _org2src, _src2files


def get_multiple_kplets():



if __name__ == '__main__':

    kplets_ranked = get_heavy_archaea_kplets()

    # for kplet in kplets_ranked[:100]:
    #     print kplet