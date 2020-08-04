# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


def fix_fk(cr, target):
    for table, column, constraint_name, delete_action in util.get_fk(cr, target, quote_ident=False):
        # Skip some already fixed fields
        if (table, column) not in [
            ("account_invoice_account_move_line_rel", "account_invoice_id"),
            ("account_invoice_account_move_line_rel", "account_invoice_id"),
            ("account_invoice_line", "invoice_id"),
            ("account_invoice", "refund_invoice_id"),
            ("account_invoice_tax", "invoice_id"),
            ("account_invoice_line_tax", "invoice_line_id"),
            ("account_invoice", "auto_invoice_id"),  # defined (and handled) in inter_company_rules
        ]:
            old_column = "{}_mig_s124".format(column)
            cr.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{column}" TO "{old_column}"')
            util.create_column(cr, table, column, "int4")


def migrate(cr, version):
    fix_fk(cr, "account_invoice")
    fix_fk(cr, "account_invoice_line")
