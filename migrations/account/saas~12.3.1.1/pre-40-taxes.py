# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # These two tables are used to migrate financial tags ; they can be filled in
    # pre script by l10n modules if needed (see l10n_es for an example)
    if util.table_exists(cr, "tax_accounts_v12_bckp"):
        cr.execute(
            """
            CREATE TABLE financial_tags_conversion_map(
                old_tag_name VARCHAR,
                new_tag_name VARCHAR,
                invoice_type VARCHAR,
                repartition_type VARCHAR,
                module VARCHAR
            );
        """
        )

        cr.execute(
            """
            CREATE TABLE v12_financial_tags_registry(
                tag_id INTEGER REFERENCES account_account_tag(id))
        """
        )

        # This table is used to store the group taxes that should not be merged with their children
        # into a single tax
        cr.execute(
            """
            CREATE TABLE taxes_not_to_merge(
                tax_id INTEGER REFERENCES account_tax(id)
            );
        """
        )

    # This table is used for migrating cash basis taxes, since we need to know the
    # type and journal of each original invoice in order to apply tags to their cash
    # basis entries properly.
    cr.execute("""
        CREATE TABLE caba_aml_invoice_info
        AS SELECT caba_aml.id AS aml_id, invoice.type AS invoice_type, invoice_journal.type AS journal_type
        FROM account_move_line caba_aml
        JOIN res_company company ON company.id = caba_aml.company_id AND company.tax_exigibility
        JOIN account_move caba_move ON caba_move.id = caba_aml.move_id
        JOIN account_partial_reconcile caba_partial_rec ON caba_partial_rec.id = caba_move.tax_cash_basis_rec_id
        JOIN account_move_line invoice_aml ON invoice_aml.id IN (caba_partial_rec.credit_move_id, caba_partial_rec.debit_move_id)
        JOIN account_journal invoice_journal ON invoice_journal.id = invoice_aml.journal_id AND invoice_journal.type in ('sale', 'purchase')
        JOIN account_invoice invoice ON invoice.id = invoice_aml.invoice_id
    """)
