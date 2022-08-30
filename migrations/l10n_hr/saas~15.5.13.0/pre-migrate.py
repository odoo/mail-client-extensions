# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "l10n_hr.account_reports_hr_statements_menu")])
