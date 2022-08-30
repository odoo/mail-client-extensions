# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "l10n_de.account_reports_de_statements_menu")])
