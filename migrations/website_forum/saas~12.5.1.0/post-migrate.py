# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Give a name to forum posts that were created from a comment
    # See https://github.com/odoo/odoo/pull/45159
    cr.execute("""
        UPDATE forum_post p
            SET name = 'Re: ' || COALESCE(q.name, '')
            FROM forum_post q
            WHERE p.name IS NULL
                AND q.id = p.parent_id
    """)
