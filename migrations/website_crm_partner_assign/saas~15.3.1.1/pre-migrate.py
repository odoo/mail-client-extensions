# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.partner", "implemented_count", "implemented_partner_count")
