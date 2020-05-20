# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_crm.view_quotation_tree")
    util.remove_view(cr, "sale_crm.view_order_tree")
