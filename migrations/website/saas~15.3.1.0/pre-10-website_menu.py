# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "website.menu", "group_ids")
    util.remove_record(cr, "website.website_menu")
