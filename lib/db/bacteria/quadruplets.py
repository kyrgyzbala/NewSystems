__author__ = 'Sanjarbek Hudaiberdiev'

from lib.db import DbClass


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


def store_kplets_pile(kplets_pile, cdd2id, file2id):

    _sql_kplet = """insert ignore into bacteria_4plets (kplet_1, kplet_2, kplet_3, kplet_4) values \n"""

    _sql_kplet_file = """insert ignore into bacteria_4plets_win10 (kplet_id, file_id) values \n"""

    for (kplets, fname) in kplets_pile:

        for kplet in kplets:
            kplet = list(kplet)
            kplet.sort()
            kplet = tuple([int(cdd2id[k]) for k in kplet])

            _sql_kplet += """(%d, %d, %d, %d),\n""" % kplet

            _sql_kplet_file += ("""((select id from bacteria_4plets where """ +
                                """kplet_1=%d and kplet_2=%d and kplet_3=%d and kplet_4=%d),""" +
                                """%d),\n""") % (kplet + (int(file2id[fname]),))

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
