# -*- coding: utf-8 -*-
import logging
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.account.9.0.'
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):

    # Delete all account_move_line whose period has the flag 'special' (opening and closing period) set to True
    cr.execute("""DELETE FROM account_move_line
                    WHERE id IN (SELECT aml.id FROM account_move_line AS aml, account_period AS p, account_journal AS j
                       WHERE p.id = aml.period_id AND aml.journal_id = j.id
                        AND p.special = True AND j.type = 'situation')
                """)

    # Delete account of type = view and consolidation
    # first remove foreign key constraint that says on delete cascade on parent_id
    cr.execute("""ALTER TABLE account_account DROP CONSTRAINT IF EXISTS
                    "account_account_parent_id_fkey"
                """)

    cr.execute("""DELETE FROM account_tax AS t
                        USING account_account AS a
                        WHERE (t.account_collected_id = a.id OR t.account_paid_id = a.id)
                          AND a.type IN ('view', 'consolidation')
                    RETURNING t.name
    """)
    for tax_name in cr.fetchall():
        _logger.info("deleted unusable tax %s", tax_name)

    cr.execute("""DELETE FROM account_account
                    WHERE type in ('view', 'consolidation')
                """)

    # We don't have the state field on aml anymore, and aml with state draft have no reason to exists so we delete them
    # If we don't, some reports will be wrong
    cr.execute("""DELETE FROM account_move_line
                    WHERE state = 'draft'
                """)

    # Delete some view(s) that are not used anymore
    util.remove_view(cr, xml_id="account.view_account_journal_1")
    util.remove_view(cr, xml_id="account.partner_view_button_journal_item_count")
    util.remove_view(cr, xml_id="account.view_bank_statement_form2")
    util.remove_view(cr, xml_id="account.view_account_period_form")
    util.force_noupdate(cr, 'account.invoice_form', False)
    util.force_noupdate(cr, 'account.view_account_invoice_filter', False)

    # remove all element related to template, they will be recreated with the localization
    cr.execute("""
       DELETE FROM account_fiscal_position_tax_template;
       DELETE FROM account_fiscal_position_account_template;
       DELETE FROM account_fiscal_position_template;
       DELETE FROM account_tax_template;
       DELETE FROM account_account_template;
    """)
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model IN ('account.fiscal.position.tax.template',
                              'account.fiscal.position.account.template',
                              'account.fiscal.position.template',
                              'account.tax.template',
                              'account.account.template')
    """)
