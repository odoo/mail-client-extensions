# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.report_mrp_bom_line")
    util.remove_view(cr, "mrp.report_mrp_operation_line")
    util.remove_view(cr, "mrp.report_mrp_byproduct_line")
    util.remove_view(cr, "mrp.report_mrp_bom_pdf")
