# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "website_sale_dashboard.sale_dashboard_view")
