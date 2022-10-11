# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_plm.message_approval")
    util.remove_view(cr, "mrp_plm.report_mrp_bom_line_inherit_mrp_plm")
