# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "forum_forum", "sequence", "int4")
    util.create_column(cr, "forum_forum", "mode", "varchar")
    cr.execute("UPDATE forum_forum SET sequence=id, mode='discussions'")

    util.remove_view(cr, "website_forum.res_users_view_form_preference")
    util.remove_view(cr, "website_forum.forum_user_tooltip")
