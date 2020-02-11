# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "forum_forum", "privacy", "varchar")
    util.create_column(cr, "forum_forum", "authorized_group_id", "int4")
    util.create_column(cr, "forum_forum", "menu_id", "int4")
    cr.execute("UPDATE forum_forum SET privacy='public'")
