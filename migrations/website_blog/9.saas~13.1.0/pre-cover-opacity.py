# -*- coding: utf-8 -*-
import json

def migrate(cr, version):
    # See https://github.com/odoo/odoo/commit/74d7de465e38dc6a16aa6e395aa733ddb2e01240
    cr.execute("SELECT id, cover_properties FROM blog_post")
    for post_id, cover in cr.fetchall():
        cover = json.loads(cover)
        if cover.get('background-color') != 'oe_none':
            cover['opacity'] = '0.6'
        else:
            cover['opacity'] = '%.2f' % (1.0 - float(cover['opacity']),)

        cr.execute("UPDATE blog_post SET cover_properties=%s WHERE id=%s",
                   [json.dumps(cover), post_id])
