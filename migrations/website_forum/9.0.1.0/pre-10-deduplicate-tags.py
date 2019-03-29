# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # temporarily allow duplicated tags per post
    cr.execute("ALTER TABLE forum_tag_rel DROP CONSTRAINT forum_tag_rel_forum_id_forum_tag_id_key")

    cr.execute("""SELECT array_agg(id) as ids
                    FROM forum_tag
                   GROUP BY forum_id, trim(lower(name))
                  HAVING COUNT(id) > 1""")

    todel = []
    for row in cr.fetchall():
        ids = row[0]
        ids.sort()
        cid, other_ids = ids[0], ids[1:]
        todel.extend(other_ids)

        for oid in other_ids:
            util.replace_record_references(cr, ('forum.tag', oid), ('forum.tag', cid))

    if todel:
        cr.execute('DELETE FROM forum_tag WHERE id IN %s', [tuple(todel)])
        util.fixup_m2m(cr, 'forum_tag_rel',
                          'forum_post', 'forum_tag', 'forum_id', 'forum_tag_id')

    cr.execute("UPDATE forum_tag SET name = trim(name)")
