# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "repair.line", ["price_total"])
    util.recompute_fields(cr, "repair.fee", ["price_total"])
