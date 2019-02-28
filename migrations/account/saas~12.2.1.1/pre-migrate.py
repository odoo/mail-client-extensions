# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.invoice.line", "product_image")

    cr.execute(
        """
        UPDATE account_payment_term_line
           SET "option" = 'day_following_month'
         WHERE "option" = 'after_invoice_month'
    """
    )

    util.create_column(cr, "account_move_line", "reconcile_model_id", "int4")

    for table in {"account_move", "account_reconcile_model", "account_reconcile_model_template"}:
        util.create_column(cr, table, "to_check", "boolean")
        cr.execute("UPDATE {} SET to_check = FALSE".format(table))

    cr.execute("ALTER TABLE res_company ALTER COLUMN fiscalyear_last_month TYPE varchar")

    util.move_field_to_module(cr, "res.company", "sale_note", "sale", "account")
    util.rename_field(cr, "res.company", "sale_note", "invoice_terms")
    util.move_field_to_module(cr, "res.config.settings", "sale_note", "sale", "account")
    util.rename_field(cr, "res.config.settings", "sale_note", "invoice_terms")
    util.move_field_to_module(cr, "res.config.settings", "use_sale_note", "sale", "account")
    util.rename_field(cr, "res.config.settings", "use_sale_note", "use_invoice_terms")
    cr.execute(
        """
        UPDATE ir_config_parameter
           SET "key" = 'account.use_invoice_terms'
         WHERE "key" = 'sale.use_sale_note'
    """
    )

    util.remove_record(cr, "account.action_bank_reconcile_bank_statements")
