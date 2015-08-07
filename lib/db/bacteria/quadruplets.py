__author__ = 'Sanjarbek Hudaiberdiev'

from lib.db import DbClass
import sys

def get_multiple_kplets():

    _cursor = setup_cursor()
    _sql_cmd = """SET group_concat_max_len=15000"""
    _cursor.execute(_sql_cmd)

    _sql_cmd = """select  ap.id, count(*) cnt, group_concat(convert(apw.file_id, char(15))) as file_ids
                  from bacteria_5plets ap
                  inner join bacteria_5plets_win10 apw on ap.id = apw.kplet_id
                  group by ap.id
                  having count(*)>1
                  order by cnt desc"""

    _cursor.execute(_sql_cmd)

    return _cursor.fetchall()


# def insert_kplet(kplet_codes, fname):
#
#     kplet_codes = tuple(kplet_codes)
#     _db = DbClass()
#     _db.cmd = """insert ignore into bacteria_4plets (kplet_1, kplet_2, kplet_3, kplet_4)
#                  values (
#                   (select id from cdd_profiles where code='%s'),
#                   (select id from cdd_profiles where code='%s'),
#                   (select id from cdd_profiles where code='%s'),
#                   (select id from cdd_profiles where code='%s'))""" % kplet_codes
#
#     _db.execute()
#     _db.commit()
#
#     _db.cmd = """insert ignore into bacteria_4plets_win10 (kplet_id, file_id) values (
#                  (select id from bacteria_4plets where kplet_1=(select id from cdd_profiles where code='%s')
#                                                     and kplet_2=(select id from cdd_profiles where code='%s')
#                                                     and kplet_3=(select id from cdd_profiles where code='%s')
#                                                     and kplet_4=(select id from cdd_profiles where code='%s')),
#                  (select id from bacteria_win10_files where name='%s'))""" % (kplet_codes + (fname,))
#
#     _db.execute()
#     _db.commit()


def store_kplets(kplets, fname):

    _sql_kplet = """insert ignore into bacteria_4plets (kplet_1, kplet_2, kplet_3, kplet_4) values \n"""

    _sql_kplet_file = """insert ignore into bacteria_4plets_win10 (kplet_id, file_id) values \n"""

    for kplet in kplets:
        kplet = list(kplet)
        kplet.sort()
        kplet = tuple(kplet)
        _sql_kplet += ("""((select id from cdd_profiles where code='%s'),""" +
                       """(select id from cdd_profiles where code='%s'),""" +
                       """(select id from cdd_profiles where code='%s'),""" +
                       """(select id from cdd_profiles where code='%s')),\n""") % kplet

        _sql_kplet_file += ("""((select id from bacteria_4plets where """ +
                            """kplet_1=(select id from cdd_profiles where code='%s') """ +
                            """and kplet_2=(select id from cdd_profiles where code='%s') """ +
                            """and kplet_3=(select id from cdd_profiles where code='%s') """ +
                            """and kplet_4=(select id from cdd_profiles where code='%s')),""" +
                            """(select id from bacteria_win10_files where name='%s')),\n""") % (kplet + (fname,))

    _sql_kplet = _sql_kplet[:-2]
    _sql_kplet += ';'

    _sql_kplet_file = _sql_kplet_file[:-2]
    _sql_kplet_file += ';'

    _db = DbClass()

    _db.cmd = _sql_kplet
    _db.execute()

    _db.cmd = _sql_kplet_file
    _db.execute()



def store_kplets_pile(kplets_pile):

    _sql_kplet = """insert ignore into bacteria_4plets (kplet_1, kplet_2, kplet_3, kplet_4) values \n"""

    _sql_kplet_file = """insert ignore into bacteria_4plets_win10 (kplet_id, file_id) values \n"""

    for (kplets, fname) in kplets_pile:

        for kplet in kplets:
            kplet = list(kplet)
            kplet.sort()
            kplet = tuple(kplet)
            _sql_kplet += ("""((select id from cdd_profiles where code='%s'),""" +
                           """(select id from cdd_profiles where code='%s'),""" +
                           """(select id from cdd_profiles where code='%s'),""" +
                           """(select id from cdd_profiles where code='%s')),\n""") % kplet

            _sql_kplet_file += ("""((select id from bacteria_4plets where """ +
                                """kplet_1=(select id from cdd_profiles where code='%s') """ +
                                """and kplet_2=(select id from cdd_profiles where code='%s') """ +
                                """and kplet_3=(select id from cdd_profiles where code='%s') """ +
                                """and kplet_4=(select id from cdd_profiles where code='%s')),""" +
                                """(select id from bacteria_win10_files where name='%s')),\n""") % (kplet + (fname,))

    _sql_kplet = _sql_kplet[:-2]
    _sql_kplet += ';'

    _sql_kplet_file = _sql_kplet_file[:-2]
    _sql_kplet_file += ';'

    _db = DbClass()

    fout = open('insert_kplet.sql','w')
    [fout.write(l) for l in _sql_kplet]
    fout.close()

    print 'Inserting kplets'
    _db.cmd = _sql_kplet
    _db.execute()
    _db.commit()

    print 'inserting kplet files'
    _db.cmd = _sql_kplet_file
    _db.execute()
    _db.commit()



def get_report_kplets():

    cursor = setup_cursor()
    sql_cmd = """SET group_concat_max_len=15000"""
    cursor.execute(sql_cmd)

    sql_cmd = """select apc.*, s1.cnt, s1.wgt, s1.an
                from (
                        select ap.id ,count(*) as cnt, sum(w.weight) as wgt, group_concat(awf.name) as an
                        from bacteria_5plets ap
                        inner join bacteria_5plets_win10 apw on ap.id = apw.kplet_id
                        inner join bacteria_win10_files awf on apw.file_id = awf.id
                        inner join sources s on awf.source_id=s.id
                        inner join weights w on w.genome_id=s.genome_id
                        group by ap.id
                        having count(distinct s.genome_id)>1 ) s1
                inner join bacteria_5plets_codes apc on s1.id=apc.id
                order by s1.wgt desc
                limit 0,300"""

    cursor.execute(sql_cmd)

    out_list = []

    for row in cursor.fetchall():
        id = row[0]
        kplet_codes = (row[1:6])
        count = row[6]
        weight = row[7]
        files = row[8]
        out_list.append([id, kplet_codes, count, weight, files])

    return out_list