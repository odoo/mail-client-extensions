# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "is_tax_closing", "boolean")
    util.create_column(cr, "res_company", "account_tax_periodicity", "varchar")
    util.create_column(cr, "res_company", "account_tax_periodicity_reminder_day", "int4")
    util.create_column(cr, "res_company", "account_tax_original_periodicity_reminder_day", "int4")
    util.create_column(cr, "res_company", "account_tax_periodicity_journal_id", "int4")
    util.create_column(cr, "res_company", "account_tax_next_activity_type", "int4")

    cr.execute("""
        UPDATE res_company
           SET account_tax_periodicity='monthly',
               account_tax_periodicity_reminder_day=7
    """)
