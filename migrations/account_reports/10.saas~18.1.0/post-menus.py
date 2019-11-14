# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "account_reports.account_reports_business_statements_menu")])
