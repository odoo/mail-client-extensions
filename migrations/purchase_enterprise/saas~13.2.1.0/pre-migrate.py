# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_enterprise.view_purchase_order_search_inherit")
