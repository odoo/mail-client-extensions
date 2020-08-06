# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-13.4.1.1" + __name__)


def migrate(cr, version):
    env = util.env(cr)

    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    # Fix default suspense account for res.company that is the account used as counterpart on draft bank statement lines.

    for company in env['res.company'].search([]):
        company.account_journal_suspense_account_id = env['account.chart.template']._create_liquidity_journal_suspense_account(
            company,
            company.chart_template_id.code_digits or 6,
        )

    # Fix additional 'payment_debit_account_id', 'payment_credit_account_id', 'suspense_account_id' on account.journal.
    # payment_debit_account_id/payment_credit_account_id are the new accounts used by the account.payments instead of
    # default_debit_account_id/default_credit_account_id.
    # suspense_account_id is the same as the one set on the company but allowing to have a custom one by journal.

    current_assets_type = env.ref('account.data_account_type_current_assets')
    for journal in env['account.journal'].search([('type', 'in', ('bank', 'cash'))]):
        digits = journal.company_id.chart_template_id.code_digits or 6

        if journal.type == 'bank':
            liquidity_account_prefix = journal.company_id.bank_account_code_prefix or ''
        else:
            liquidity_account_prefix = journal.company_id.cash_account_code_prefix or journal.company_id.bank_account_code_prefix or ''

        journal.write({
            'payment_debit_account_id': env['account.account'].create({
                'name': "Outstanding Receipts",
                'code': env['account.account']._search_new_account_code(journal.company_id, digits, liquidity_account_prefix),
                'reconcile': True,
                'user_type_id': current_assets_type.id,
                'company_id': journal.company_id.id,
            }).id,
            'payment_credit_account_id': env['account.account'].create({
                'name': "Outstanding Payments",
                'code': env['account.account']._search_new_account_code(journal.company_id, digits, liquidity_account_prefix),
                'reconcile': True,
                'user_type_id': current_assets_type.id,
                'company_id': journal.company_id.id,
            }).id,
            'suspense_account_id': journal.company_id.account_journal_suspense_account_id.id,
        })

    # Create account.move for 'draft' statement line.

    cr.execute('''
        SELECT 
            st_line_backup.move_name AS name,
            st_line_backup.ref,
            st_line_backup.date,
            st_line_backup.note AS narration,
            st_line_backup.id AS statement_line_id,
            st_line_backup.journal_id,
            st_line_backup.partner_id,
            COALESCE(journal.currency_id, company.currency_id) AS currency_id
        FROM account_bank_statement_line_pre_backup st_line_backup
        JOIN account_bank_statement_line st_line ON st_line.id = st_line_backup.id
        JOIN account_journal journal ON journal.id = st_line.journal_id
        JOIN res_company company ON company.id = journal.company_id
        WHERE st_line.move_id IS NULL
    ''')

    moves = env['account.move'].with_context(skip_account_move_synchronization=True).create(cr.dictfetchall())

    # Link newly created account.move to existing draft account.bank.statement.line.
    cr.executemany(
        "UPDATE account_bank_statement_line SET move_id = %s WHERE id = %s",
        [(move.id, move.statement_line_id.id) for move in moves],
    )

    if moves:
        # Update the newly created account.move from the "old" account.bank.statement.line model.
        cr.execute('''
            UPDATE account_move move
            SET currency_id = COALESCE(journal.currency_id, company.currency_id),
                partner_id = st_line_backup.partner_id,
                partner_bank_id = st_line_backup.bank_account_id,
                journal_id = st_line_backup.journal_id,
                ref = st_line_backup.ref,
                narration = st_line_backup.note,
                company_id = st_line_backup.company_id
            FROM account_bank_statement_line_pre_backup st_line_backup
            JOIN account_bank_statement_line st_line ON st_line.id = st_line_backup.id
            JOIN account_journal journal ON journal.id = st_line_backup.journal_id
            JOIN res_company company ON company.id = journal.company_id
            WHERE move.id = st_line.move_id
            AND move.id IN %s
        ''', [tuple(moves.ids)])

        # Create the account.move.line for newly created account.move.
        moves.invalidate_cache()

        move_lines_to_create = []
        for move in moves:
            for vals in move.statement_line_id._prepare_move_line_default_vals():
                move_lines_to_create.append({**vals, 'move_id': move.id})
        env['account.move.line'].with_context(skip_account_move_synchronization=True).create(move_lines_to_create)

    # 'statement_line_id' on account.move.line is now a related field.
    # 'statement_id' must be updated because it's a related 'statement_line_id.statement_id'.

    cr.execute('''
        UPDATE account_move_line
        SET statement_line_id = move.statement_line_id,
            statement_id = st_line.statement_id
        FROM account_move move
        JOIN account_bank_statement_line st_line ON st_line.id = move.statement_line_id
        WHERE account_move_line.move_id = move.id
    ''')

    # Post all bank statements that seem to be already processed meaning the balance_end & balance_end_real must be
    # the same and not be part of a broken statement chain.

    env['account.bank.statement'].search([('is_valid_balance_start', '=', True), ('difference', '=', 0.0)]).button_post()

    # Change the liquidity account of payments that are not yet reconciled with a statement line.
    # This should be done because the payment is no longer impacting directly the bank/cash account like the
    # statement line does. Instead, we use a temporary liquidity account.
    # To work retroactively, this must be done only on journal entry that are not shared between
    # an account.bank.statement.line and an account.payment.
    # This part is done in 'post' because new account.account are created in 'post' to migrate
    # the account.journal.

    cr.execute('''
        UPDATE account_move_line line
        SET account_id = CASE WHEN line.balance < 0.0 THEN journal.payment_debit_account_id ELSE journal.payment_credit_account_id END
        FROM account_payment pay
        JOIN account_move move ON move.id = pay.move_id
        JOIN account_journal journal ON journal.id = move.journal_id
        WHERE move.statement_line_id IS NULL
        AND line.move_id = move.id
        AND line.account_id IN (journal.default_debit_account_id, journal.default_credit_account_id)
    ''')

    # Create account.move for draft/cancel payments.

    cr.execute('''
        SELECT
            pay_backup.move_name AS name,
            pay_backup.journal_id,
            pay_backup.id AS payment_id,
            pay_backup.payment_date AS date,
            pay_backup.partner_id,
            pay_backup.currency_id
        FROM account_payment_pre_backup pay_backup
        JOIN account_payment pay ON pay.id = pay_backup.id
        WHERE pay_backup.state IN ('draft', 'cancelled')
        AND pay.move_id IS NULL
    ''')
    moves = env['account.move'].with_context(skip_account_move_synchronization=True).create(cr.dictfetchall())

    cr.executemany('''
        UPDATE account_payment
        SET move_id = %s
        WHERE id = %s
    ''', [(move.id, move.payment_id.id) for move in moves])

    moves.invalidate_cache()
    move_lines_to_create = []
    for move in moves:
        for vals in move.payment_id._prepare_move_line_default_vals():
            move_lines_to_create.append({**vals, 'move_id': move.id})
    env['account.move.line'].with_context(skip_account_move_synchronization=True).create(move_lines_to_create)

    cr.execute("SELECT id FROM account_payment_pre_backup pay_backup WHERE state = 'cancelled'")

    res_ids = [res[0] for res in cr.fetchall()]
    if res_ids:
        env['account.payment'].browse(res_ids).action_cancel()

    # Since the 'post_at' field is gone, post the journal entries that are reconciled and still in draft.

    cr.execute('''
        SELECT DISTINCT move.id
        FROM account_partial_reconcile part
        JOIN account_move_line line ON 
            line.id = part.debit_move_id
            OR 
            line.id = part.credit_move_id
        JOIN account_move move ON move.id = line.move_id
        WHERE move.state = 'draft'
    ''')

    env['account.move'].browse(row[0] for row in cr.fetchall()).action_post()

    # 'payment_id' on account.move.line is now a related field.

    cr.execute('''
        UPDATE account_move_line
        SET payment_id = move.payment_id
        FROM account_move move
        WHERE move.payment_id IS NOT NULL
        AND account_move_line.move_id = move.id
    ''')

    # ==== CHECK move_id that must be set on all account.payment/account.bank.statement.line ====

    cr.execute("SELECT id FROM account_payment WHERE move_id IS NULL")
    for payment_id in cr.fetchall():
        _logger.error("Missing move_id on account.payment (id=%s)" % payment_id)

    cr.execute("SELECT id FROM account_bank_statement_line WHERE move_id IS NULL")
    for st_line_id in cr.fetchall():
        _logger.error("Missing move_id on account.bank.statement.line (id=%s)" % st_line_id)
