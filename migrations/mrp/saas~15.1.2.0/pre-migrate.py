# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mrp.label_production_order")
    util.remove_view(cr, "mrp.report_reception_report_label_mrp")
