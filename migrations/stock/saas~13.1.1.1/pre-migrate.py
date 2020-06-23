# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "report.stock.forecast")
    util.remove_model(cr, "stock.overprocessed.transfer")
    util.remove_model(cr, "stock.picking.responsible")
