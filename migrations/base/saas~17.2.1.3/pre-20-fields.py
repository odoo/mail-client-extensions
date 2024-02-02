# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.company", "country_code", "account", "base")
