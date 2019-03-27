# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    gone = util.splitlines("""
        badge_form_view_forum
        badge
        users
        private_profile     # too different, recreate it
        edit_profile
        user_detail_full
        user_badges
    """)
    for v in gone:
        util.remove_view(cr, "website_forum." + v)
