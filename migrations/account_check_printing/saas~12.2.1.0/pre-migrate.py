# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "account_register_payments"):
        cr.execute("ALTER TABLE account_register_payments ALTER COLUMN check_number TYPE varchar")
    cr.execute("ALTER TABLE account_payment ALTER COLUMN check_number TYPE varchar")
    cr.execute("ALTER TABLE print_prenumbered_checks ALTER COLUMN next_check_number TYPE varchar")
