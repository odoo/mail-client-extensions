# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===========================================================
    # QR codes (PR:44839)
    # ===========================================================
    util.create_column(cr, "account_move", "qr_code_method", "varchar")
    util.create_column(cr, "res_company", "qr_code", "boolean")

    # ===========================================================
    # Incoterms (PR:43883)
    # ===========================================================

    util.rename_field(cr, "account.move", "type", "move_type")
    util.rename_field(cr, "account.invoice.report", "type", "move_type")
    util.rename_field(cr, "account.move.line", "tag_ids", "tax_tag_ids")

    incoterm_codes = "DAF,DES,DEQ,DDU,DAT".split(",")

    for code in incoterm_codes:
        util.force_noupdate(cr, "account.incoterm_%s" % code)

    cr.execute(
        """
        UPDATE account_incoterms
        set active = 'f'
        where id in %s
    """,
        [tuple(util.ref(cr, "account.incoterm_%s" % code) for code in incoterm_codes)],
    )

    # ===========================================================
    # Internal Transfer (PR:45812 & 8595)
    # ===========================================================

    util.remove_field(cr, 'account.payment', 'destination_journal_id')
    util.create_column(cr, 'account_payment', 'is_internal_transfer', 'boolean')
    cr.execute("""
    UPDATE account_payment
       SET is_internal_transfer = (payment_type = 'transfer')
    """)
    # change payment_type from 'transfer' to 'inbound', update partner_id & move_name
    cr.execute("""
    UPDATE account_payment pay
       SET payment_type = 'outbound',
           partner_id = comp.partner_id,
           move_name = split_part(pay.move_name, '§§', 1)
      FROM account_journal journal
      JOIN res_company comp ON comp.id = journal.company_id
     WHERE journal.id = pay.journal_id
       AND pay.payment_type = 'transfer'
    """)

    # ===========================================================
    # Account Security (PR:46586 & 8986)
    # ===========================================================

    # Add new company_id stored fields.

    util.create_column(cr, 'account_reconcile_model_line', 'company_id', 'int4')

    cr.execute('''
        UPDATE account_reconcile_model_line line
        SET company_id = model.company_id
        FROM account_reconcile_model model
        WHERE model.id = line.model_id
    ''')

    util.create_column(cr, 'account_fiscal_position_tax', 'company_id', 'int4')

    cr.execute('''
         UPDATE account_fiscal_position_tax fpos_tax
         SET company_id = fpos.company_id
         FROM account_fiscal_position fpos
         WHERE fpos.id = fpos_tax.position_id
    ''')

    util.create_column(cr, 'account_fiscal_position_account', 'company_id', 'int4')

    cr.execute('''
         UPDATE account_fiscal_position_account fpos_account
         SET company_id = fpos.company_id
         FROM account_fiscal_position fpos
         WHERE fpos.id = fpos_account.position_id
    ''')

    util.create_column(cr, 'account_payment', 'company_id', 'int4')

    cr.execute('''
        UPDATE account_payment pay
        SET company_id = journal.company_id
        FROM account_journal journal
        WHERE journal.id = pay.journal_id
    ''')

    util.create_column(cr, 'account_move_reversal', 'company_id', 'int4')
    util.convert_field_to_property(cr, 'account.cash.rounding', 'profit_account_id', 'many2one',
                                   target_model='account.account', company_field='NULL')
    util.convert_field_to_property(cr, 'account.cash.rounding', 'loss_account_id', 'many2one',
                                   target_model='account.account', company_field='NULL')

    # Check for existing multi-company issues.

    fields_to_check = {
        'account.account': ['tax_ids'],
        'account.journal.group': ['excluded_journal_ids'],
        'account.journal': [
            'account_control_ids', 'default_credit_account_id', 'default_debit_account_id', 'profit_account_id',
            'loss_account_id', 'bank_account_id', 'secure_sequence_id',
        ],
        'account.tax': ['children_tax_ids', 'cash_basis_transition_account_id', 'cash_basis_base_account_id'],
        'account.tax.repartition.line': ['account_id', 'invoice_tax_id', 'refund_tax_id'],
        'account.analytic.line': ['move_id'],
        'account.bank.statement': ['journal_id'],
        'account.bank.statement.line': ['account_id', 'statement_id'],
        'account.move': [
            'journal_id', 'reversed_entry_id', 'fiscal_position_id', 'invoice_payment_term_id',
            'invoice_partner_bank_id',
        ],
        'account.move.line': [
            'move_id', 'journal_id', 'account_id', 'reconcile_model_id', 'payment_id', 'statement_line_id',
            'tax_ids', 'tax_repartition_line_id', 'analytic_account_id', 'analytic_tag_ids',
        ],
        'account.payment': ['journal_id', 'partner_bank_account_id', 'invoice_ids'],
        'account.reconcile.model.line': [
            'account_id', 'journal_id', 'tax_ids', 'analytic_account_id', 'analytic_tag_ids',
        ],
        'account.reconcile.model': ['match_journal_ids'],
        'account.fiscal.position.tax': ['tax_src_id', 'tax_dest_id'],
        'account.fiscal.position.account': ['account_src_id', 'account_dest_id'],
    }

    for model_name, field_names in fields_to_check.items():
        for field_name in field_names:
            util.check_company_fields(cr, model_name, field_name)

    util.create_column(cr, 'account_tax_repartition_line', 'use_in_tax_closing', 'bool')

    cr.execute(
       """
         UPDATE account_tax_repartition_line
            SET use_in_tax_closing = TRUE
           FROM account_account
          WHERE account_tax_repartition_line.account_id = account_account.id
        AND NOT account_account.internal_group IN ('income', 'expense')
           """
          )
    cr.execute(
       """
         UPDATE account_tax_repartition_line
            SET use_in_tax_closing = FALSE
          WHERE use_in_tax_closing IS NULL
           """
          )

    util.create_column(cr, "account_move_reversal", "date_mode", "varchar")
    cr.execute("UPDATE account_move_reversal SET date_mode = 'custom' WHERE date_mode IS NULL")
