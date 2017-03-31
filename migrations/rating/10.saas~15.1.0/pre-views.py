# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'rating.assets_backend')

    for view in 'kanban pivot graph search'.split():
        util.rename_xmlid(cr, 'rating.view_rating_rating_' + view,
                          'rating.rating_rating_view_' + view)

    toupdate = util.splitlines("""
        rating_external_page_view
        rating_external_page_submit
        rating_rating_view_kanban
        action_view_rating
    """)
    for t in toupdate:
        util.force_noupdate(cr, 'rating.' + t, False)
