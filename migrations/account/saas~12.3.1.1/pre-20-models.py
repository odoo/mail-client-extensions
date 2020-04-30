# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_account_tag", "tax_negate", "boolean")
    util.create_column(cr, "account_account_tag", "country_id", "int4")
    util.create_column(cr, "account_journal", "invoice_reference_type", "varchar")
    util.create_column(cr, "account_journal", "invoice_reference_model", "varchar")
    cr.execute(
        """
        UPDATE account_journal
           SET invoice_reference_type='invoice',
               invoice_reference_model='odoo'
    """
    )

    util.rename_field(cr, "account_tax", "cash_basis_account_id", "cash_basis_transition_account_id")
    if util.table_exists(cr, "tax_accounts_v12_bckp"):
        cr.execute(
            """
            UPDATE tax_accounts_v12_bckp
               SET account_id = account_tax.cash_basis_transition_account_id
              FROM account_tax
             WHERE account_tax.id = tax_accounts_v12_bckp.id
               AND account_tax.cash_basis_transition_account_id is not null;

            UPDATE account_tax
               SET cash_basis_transition_account_id = account_id, account_id = cash_basis_transition_account_id
             WHERE cash_basis_transition_account_id is not null;
        """
        )

    for table in ("account_invoice_tax", "account_move_line"):
        util.create_column(cr, table, "tax_repartition_line_id", "int4")
        cr.execute("CREATE INDEX ON %s(tax_repartition_line_id)" % table)
    util.create_column(cr, "account_move_line", "tax_line_id", "int4")
    util.create_m2m(cr, "account_invoice_tax_account_tax", "account_invoice_tax", "account_tax")
    util.create_m2m(cr, "account_invoice_tax_account_account_tag", "account_invoice_tax", "account_account_tag")
    util.create_column(cr, "account_move", "auto_post", "boolean")
    util.create_m2m(cr, "account_move_line_account_account_tag", "account_move_line", "account_account_tag")
    util.create_column(cr, "account_move_line", "tax_audit", "varchar")

    util.remove_field(cr, "account.tax", "tag_ids")

    cr.execute("CREATE INDEX ON account_invoice_tax(tax_id)")
    cr.execute("CREATE INDEX ON account_move_line(tax_line_id)")

    util.remove_model(cr, "account.abstract.payment")
    util.remove_model(cr, "account.register.payments")
