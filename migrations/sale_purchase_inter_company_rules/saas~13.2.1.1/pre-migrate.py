# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE res_company SET rule_type = applicable_on WHERE rule_type = 'so_and_po'")
    util.remove_field(cr, "res.company", "applicable_on")
    util.remove_field(cr, "res.config.settings", "applicable_on")
