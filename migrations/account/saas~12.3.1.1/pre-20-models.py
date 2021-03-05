# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_account_tag", "tax_negate", "boolean")
    util.create_column(cr, "account_account_tag", "country_id", "int4")
    util.create_column(cr, "account_journal", "invoice_reference_type", "varchar")
    util.create_column(cr, "account_journal", "invoice_reference_model", "varchar")
    cr.execute(
        """
        UPDATE account_journal j
           SET invoice_reference_type = CASE c.invoice_reference_type
                                             WHEN 'invoice_number' THEN 'invoice'
                                             ELSE c.invoice_reference_type
                                         END,
               invoice_reference_model = 'odoo'
          FROM res_company c
         WHERE c.id = j.company_id
    """
    )
    util.remove_field(cr, "res.company", "invoice_reference_type")
    util.remove_field(cr, "res.config.settings", "invoice_reference_type")

    util.rename_field(cr, "account.tax", "cash_basis_account_id", "cash_basis_transition_account_id")
    util.rename_field(cr, "account.tax.template", "cash_basis_account_id", "cash_basis_transition_account_id")

    if util.table_exists(cr, "tax_accounts_v12_bckp"):
        cr.execute(
            """
            UPDATE tax_accounts_v12_bckp
               SET account_id = account_tax.cash_basis_transition_account_id, refund_account_id=account_tax.cash_basis_transition_account_id
              FROM account_tax
             WHERE account_tax.id = tax_accounts_v12_bckp.id
               AND account_tax.cash_basis_transition_account_id is not null;

            UPDATE account_tax
               SET cash_basis_transition_account_id = account_id, account_id = cash_basis_transition_account_id, refund_account_id = cash_basis_transition_account_id
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

    cr.execute("CREATE INDEX ON account_invoice_tax(tax_id)")
    cr.execute("CREATE INDEX ON account_move_line(tax_line_id)")

    util.remove_field(cr, "account.move.line", "counterpart")

    util.remove_field(cr, "account.tax", "tag_ids")
    cr.execute("DROP TABLE IF EXISTS account_tax_account_tag CASCADE")
    util.remove_field(cr, "account.tax.template", "tag_ids")
    cr.execute("DROP TABLE IF EXISTS account_account_tag_account_tax_template_rel")

    util.remove_field(cr, "account.tax.template", "account_id")
    util.remove_field(cr, "account.tax.template", "refund_account_id")

    util.remove_field(cr, "account.payment", "multi")
    util.remove_field(cr, "account.setup.bank.manual.config", "create_or_link_option")

    util.remove_model(cr, "account.abstract.payment")
    util.remove_model(cr, "account.register.payments")
