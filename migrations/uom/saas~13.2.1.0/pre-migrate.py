# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "uom.category", "measure_type")
    util.remove_field(cr, "uom.uom", "measure_type")
