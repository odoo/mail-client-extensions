# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "account_account_type", "internal_group", "varchar")
    util.create_column(cr, "account_account", "internal_group", "varchar")
    # The second is a related stored to the previous one, no need to compute as it's always null for now

    util.create_column(cr, "account_journal", "post_at_bank_rec", "boolean")

    util.create_column(cr, "res_currency", "decimal_places", "int4")

    util.create_column(cr, "res_config_settings", "group_products_in_bills", "boolean")

    if util.module_installed(cr, "stock"):
        util.move_model(cr, "stock.incoterms", "stock", "account", move_data=True)
        util.rename_model(cr, "stock.incoterms", "account.incoterms")
        util.rename_xmlid(cr, "account.stock_incoterms_form", "account.account_incoterms_form")

    util.remove_model(cr, "wizard.multi.charts.accounts")
    util.remove_model(cr, "account.bank.accounts.wizard")
    util.remove_model(cr, "account.move.line.reconcile")
    util.remove_model(cr, "account.move.line.reconcile.writeoff")
    # reports are gone...
    util.remove_model(cr, "report.account.report_trialbalance")
    util.remove_model(cr, "account.financial.report")
    util.remove_model(cr, "report.account.report_generalledger")
    util.remove_model(cr, "report.account.report_overdue")
    util.remove_model(cr, "report.account.report_partnerledger")
    util.remove_model(cr, "report.account.report_financial")
    util.remove_model(cr, "report.account.report_tax")
    util.remove_model(cr, "accounting.report")
    util.remove_model(cr, "account.aged.trial.balance")
    util.remove_model(cr, "account.report.general.ledger")
    util.remove_model(cr, "account.report.partner.ledger")
    util.remove_model(cr, "account.tax.report")
    util.remove_model(cr, "account.balance.report")
    util.remove_model(cr, "account.common.partner.report")
    util.remove_model(cr, "account.common.account.report")

    # account.invoice.reference_type will still be used by l10n_be_invoice_bba
    util.remove_field(cr, "account.journal", "account_setup_bank_data_done")
    # `delegate=True` on the `journal_id` `many2one`
    util.remove_field(
        cr, "account.bank.statement.import.journal.creation", "account_setup_bank_data_done", drop_column=False
    )
    util.remove_field(cr, "res.company", "account_sanitize_invoice_ref")
    util.remove_field(cr, "res.company", "qr_code_payment_journal_id")
    util.remove_field(cr, "res.company", "qr_code_valid")
    util.remove_field(cr, "res.company", "account_setup_company_data_done")
    util.remove_field(cr, "res.config.settings", "module_account_batch_deposit")
    # odoo/odoo@258cd4a869673c0b25307d84bbb58655b74938b2
    util.remove_field(cr, "res.config.settings", "module_print_docsaway")
    util.remove_field(cr, "res.config.settings", "account_hide_setup_bar")
    util.remove_field(cr, "res.config.settings", "account_sanitize_invoice_ref")
    util.remove_field(cr, "res.config.settings", "qr_code_payment_journal_id")
    util.remove_field(cr, "res.config.settings", "qr_code_valid")
    util.remove_field(cr, "account.financial.year.op", "account_setup_fy_data_done")

    # set KPIs
    for kpi in {"bank_data", "fy_data", "coa"}:
        util.create_column(cr, "res_company", "account_setup_%s_state" % kpi, "varchar")
        cr.execute(
            """
            UPDATE res_company
               SET account_setup_{0}_state = CASE account_setup_{0}_done WHEN true
                                                                         THEN 'just_done'
                                                                         ELSE 'not_done'
                                              END
        """.format(
                kpi
            )
        )
        util.remove_field(cr, "res.company", "account_setup_%s_done" % kpi)

    # odoo/odoo@89e358caa8627c5eff21ee63015dece0997db2b4
    util.remove_field(cr, "res.company", "account_setup_bar_closed")

    util.create_column(cr, "res_company", "account_onboarding_invoicing_layout_state", "varchar")
    util.create_column(cr, "res_company", "account_onboarding_sample_invoice_state", "varchar")
    util.create_column(cr, "res_company", "account_onboarding_sale_tax_state", "varchar")
    cr.execute(
        """
      WITH logo_changed AS (
        SELECT c.id, a.id IS NOT NULL as changed
          FROM res_company c
     LEFT JOIN ir_attachment a
            ON a.res_model = 'res.partner'
           AND a.res_field = 'image'
           AND a.res_id = c.partner_id
           -- other logo that default ones, https://git.io/fx7os
           AND a.checksum NOT IN ('d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83',
                                  'b7de62d8497eb766f0fb39e9df4f5c237abdd29d')
      )
      UPDATE res_company c
         SET account_onboarding_invoicing_layout_state = CASE l.changed WHEN true THEN 'just_done'
                                                                                  ELSE 'not_done'
                                                          END,
             account_onboarding_sample_invoice_state =
                CASE WHEN EXISTS(SELECT 1 FROM account_invoice WHERE company_id=c.id AND sent=true)
                  THEN 'just_done'
                  ELSE 'not_done'
                END,
             account_onboarding_sale_tax_state = CASE WHEN c.account_sale_tax_id IS NOT NULL
                                                   THEN 'just_done'
                                                   ELSE 'not_done'
                                                 END
        FROM logo_changed l
       WHERE c.id = l.id
    """
    )

    util.rename_xmlid(cr, *eb("account.{stock,account}_incoterms_form"))
    util.rename_xmlid(cr, *eb("account.{stock,account}_incoterms_view_search"))

    for table in ["account_reconcile_model", "account_reconcile_model_template"]:
        util.create_column(cr, table, "rule_type", "varchar")
        util.create_column(cr, table, "auto_reconcile", "boolean")
        util.create_column(cr, table, "match_nature", "varchar")
        util.create_column(cr, table, "match_amount", "varchar")
        util.create_column(cr, table, "match_amount_min", "float8")
        util.create_column(cr, table, "match_amount_max", "float8")
        util.create_column(cr, table, "match_label", "varchar")
        util.create_column(cr, table, "match_label_param", "varchar")
        util.create_column(cr, table, "match_same_currency", "boolean")
        util.create_column(cr, table, "match_total_amount", "boolean")
        util.create_column(cr, table, "match_total_amount_param", "float8")
        util.create_column(cr, table, "match_partner", "boolean")
        cr.execute(
            """
            UPDATE {}
            SET rule_type='writeoff_button',
                match_nature='both'
        """.format(
                table
            )
        )

    if util.table_exists(cr, "account_invoice_import_wizard"):
        cr.execute("TRUNCATE account_invoice_import_wizard CASCADE")
        util.create_column(cr, "account_invoice_import_wizard", "journal_id", "int4")
