__author__ = 'Sanjarbek Hudaiberdiev'


from lib.db import DbClass
from lib.utils.classes import Kplet

import sys

def store_kplets_pile(prefix, kplets_pile, profile2id, file2id):

    kplet_table_name = "%s_2plets" % prefix
    kplet_file_table_name = "%s_2plets_files" % prefix

    _sql_kplet = """insert ignore into %s (kplet_1, kplet_2) values \n""" % kplet_table_name
    _sql_kplet_file = """insert ignore into %s (kplet_id, file_id) values \n""" % kplet_file_table_name

    for (kplets, fname) in kplets_pile:
        
        for kplet in kplets:
            kplet = list(kplet)
            kplet.sort()

            kplet = tuple([int(profile2id[k]) for k in kplet])

            _sql_kplet += """(%d, %d),\n""" % kplet

            _sql_kplet_file += ("""((select id from %s where """ +
                                """kplet_1=%d and kplet_2=%d),""" +
                                """%d),\n""") % ((kplet_table_name,) + kplet + (int(file2id[fname]),))

    _sql_kplet = _sql_kplet[:-2]
    _sql_kplet += ';'

    _sql_kplet_file = _sql_kplet_file[:-2]
    _sql_kplet_file += ';'

    _db = DbClass()

    _db.cmd = _sql_kplet
    _db.execute()
    _db.commit()

    _db.cmd = _sql_kplet_file
    _db.execute()
    _db.commit()



def get_report_kplets(prefix, id2cdd, limit_to=500):

    _db = DbClass()
    _db.cmd = """SET group_concat_max_len=1500000"""
    _db.execute()

    _db.cmd = """select cp.*, count(distinct cwf.id) as cnt, group_concat(cwf.name) as files
                from %s_2plets cp
                inner join %s_2plets_files cpw on cp.id = cpw.kplet_id
                inner join %s_files cwf on cpw.file_id = cwf.id
                group by cp.id
                having count(distinct cwf.id)>1
                order by cnt desc
                limit 0, %d""" % (prefix, prefix, prefix, limit_to)

    out_list = []

    for row in _db.retrieve():
        id = row[0]
        kplet_codes = ([id2cdd[int(_id)] for _id in row[1:3]])
        if len(set(kplet_codes)) != 2:
            continue
        count = row[3]
        files = row[4].split(',')
        tmp_kplet = Kplet(id=id, codes=kplet_codes, count=count, files=files)
        out_list.append(tmp_kplet)

    return out_list