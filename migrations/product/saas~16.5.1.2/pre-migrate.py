# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "report.product.report_producttemplatelabel")
    util.remove_view(cr, "product.report_producttemplatelabel")
