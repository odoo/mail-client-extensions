# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    if util.has_enterprise():

        # removed modules
        util.remove_module(cr, "fleet_dashboard")
        util.remove_module(cr, "im_livechat_enterprise")
        util.remove_module(cr, "purchase_stock_enterprise")
        util.remove_module(cr, "website_slides_enterprise")
        util.remove_module(cr, "web_dashboard")
