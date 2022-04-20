# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_field(cr, "website.page", "cache_time")
    util.remove_field(cr, "website.page", "cache_key_expr")
