# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):

    if util.table_exists(cr, 'im_session'):
        return

    cr.execute("CREATE TABLE im_session (id SERIAL NOT NULL, create_uid integer, PRIMARY KEY(id))")
    cr.execute("""CREATE TABLE im_session_im_user_rel(
                    im_session_id integer,
                    im_user_id integer
                  )
               """)

    util.create_column(cr, 'im_message', 'session_id', 'int4')

    # create session for each message

    cr.execute("SELECT from_id, to_id FROM im_message")
    sessions = set(map(frozenset, cr.fetchall()))

    for id1, id2 in sessions:
        cr.execute("INSERT INTO im_session (create_uid) VALUES (NULL) RETURNING id")
        sid, = cr.fetchone()
        data = dict(sid=sid, id1=id1, id2=id2)
        cr.execute("""INSERT INTO im_session_im_user_rel (im_session_id, im_user_id)
                                                  VALUES (%(sid)s, %(id1)s), (%(sid)s, %(id2)s)
                   """, data)

        cr.execute("""UPDATE im_message
                         SET session_id = %(sid)s
                       WHERE (from_id = %(id1)s AND to_id = %(id2)s)
                          OR (from_id = %(id2)s AND to_id = %(id1)s)
                   """, data)

    cr.execute("ALTER TABLE im_message DROP COLUMN to_id")
