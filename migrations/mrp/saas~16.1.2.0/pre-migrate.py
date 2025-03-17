# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "mrp.immediate.production")
    util.remove_model(cr, "mrp.immediate.production.line")
