# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "purchase_enterprise.purchase_report_menu_dashboard")])
    util.remove_record(cr, "purchase_enterprise.purchase_report_action_dashboard")
    util.remove_view(cr, "purchase_enterprise.purchase_report_view_dashboard")
