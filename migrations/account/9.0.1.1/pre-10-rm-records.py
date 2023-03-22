# -*- coding: utf-8 -*-
import logging

from openerp.tools import pickle

from openerp.addons.base.maintenance.migrations import util

NS = "openerp.addons.base.maintenance.migrations.account.9.0."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):

    # Delete all account_move_line whose period has the flag 'special' (opening and closing period) set to True
    # Ignore lines from the first opening period
    cr.execute("""DELETE FROM account_move_line
                    WHERE id IN (SELECT aml.id FROM account_move_line AS aml, account_period AS p, account_journal AS j
                       WHERE p.id = aml.period_id AND aml.journal_id = j.id
                        AND p.special = True AND j.type = 'situation'
                        AND p.id NOT IN (
                          SELECT (array_agg(id ORDER BY date_start, id))[1]
                            FROM account_period WHERE special = True GROUP BY company_id))
               """)

    # Delete account of type = view and consolidation
    # first remove foreign key constraint that says on delete cascade on parent_id
    cr.execute("""ALTER TABLE account_account DROP CONSTRAINT IF EXISTS
                    "account_account_parent_id_fkey"
                """)

    cr.execute("""
        WITH bad_taxes AS (
            SELECT t.id
              FROM account_tax t
              JOIN account_account a ON (t.account_collected_id = a.id OR t.account_paid_id = a.id)
             WHERE a.type IN ('view', 'consolidation')
        ),
        _del_fp AS (
            DELETE FROM account_fiscal_position_tax fp
                  USING bad_taxes b
                  WHERE fp.tax_dest_id = b.id
                     OR fp.tax_src_id = b.id
        )
        DELETE FROM account_tax t
              USING bad_taxes b
              WHERE b.id = t.id
          RETURNING t.id, t.name
    """)
    bad_taxes = cr.fetchall()
    bad_tax_ids = set(t[0] for t in bad_taxes)
    bad_tax_names = ', '.join(t[1] for t in bad_taxes)
    _logger.info("deleted unusable tax %s", bad_tax_names)

    cr.execute("""
        UPDATE account_account a
           SET type = 'other'
         WHERE a.type IN ('view', 'consolidation')
           AND EXISTS (
                SELECT 1
                  FROM account_invoice_tax t
                  JOIN account_invoice i ON (i.id = t.invoice_id)
                 WHERE i.state IN ('paid', 'open')
                   AND t.account_id = a.id
                 UNION
                SELECT 1
                  FROM account_invoice_line
                 WHERE account_id = a.id
                 UNION
                SELECT 1
                  FROM account_analytic_line
                 WHERE general_account_id = a.id
                 UNION
                SELECT 1
                  FROM account_fiscal_position_account
                 WHERE account_src_id = a.id
                 UNION
                SELECT 1
                  FROM account_fiscal_position_account
                 WHERE account_dest_id = a.id
           )
    """)
    cr.execute("""
        UPDATE account_account a
           SET type = CASE WHEN i.type IN ('out_invoice', 'in_refund') THEN 'receivable'
                           ELSE 'payable'
                      END
          FROM account_invoice i
         WHERE i.account_id = a.id
           AND a.type IN ('view', 'consolidation')
    """)

    cr.execute("""
        DELETE FROM account_invoice_tax AS t
              USING account_account AS a
              WHERE t.account_id = a.id
                AND a.type IN ('view', 'consolidation')
    """)

    # clean wizards
    for table in util.splitlines("""
        account_common_report
            accounting_report
            account_vat_declaration

            account_common_account_report
                account_balance_report
                account_report_general_ledger

            account_common_journal_report
                account_central_journal
                account_general_journal
                account_print_journal

            account_common_partner_report
                account_aged_trial_balance
                account_partner_ledger
                account_partner_balance


        account_addtmpl_wizard
        reconcile_account_rel
        account_automatic_reconcile

        account_move_line_reconcile_select
        account_move_line_unreconcile_select
        account_move_line_reconcile_writeoff
    """):
        cr.execute("DELETE FROM " + table)

    cr.execute("""DELETE FROM account_account
                    WHERE type in ('view', 'consolidation')
                """)

    # We don't have the state field on aml anymore, and aml with state draft have no reason to exists so we delete them
    # If we don't, some reports will be wrong
    cr.execute("""DELETE FROM account_move_line
                    WHERE state = 'draft'
                """)

    # Delete some views and records that are not used anymore
    util.remove_view(cr, "account.view_account_configuration_installer")
    util.remove_record(cr, "account.action_account_configuration_installer")
    util.remove_record(cr, "account.account_configuration_installer_todo")
    util.remove_view(cr, xml_id="account.view_account_journal_1")
    util.remove_view(cr, xml_id="account.partner_view_button_journal_item_count")
    util.remove_view(cr, xml_id="account.view_bank_statement_form2")
    util.remove_view(cr, xml_id="account.view_account_period_form")
    util.remove_view(cr, xml_id="account.view_tax_code_form")
    util.remove_view(cr, xml_id="account.account_report_general_ledger_view_inherit")
    util.force_noupdate(cr, 'account.invoice_form', False)
    util.force_noupdate(cr, 'account.view_account_invoice_filter', False)

    util.force_noupdate(cr, 'account.report_invoice', False)
    util.force_noupdate(cr, 'account.report_invoice_document', False)

    # # remove all element related to template, they will be recreated with the localization
    # cr.execute("""
    #    DELETE FROM account_fiscal_position_tax_template;
    #    DELETE FROM account_fiscal_position_account_template;
    #    DELETE FROM account_fiscal_position_template;
    #    DELETE FROM account_tax_template;
    #    DELETE FROM account_account_template;
    # """)
    # cr.execute("""
    #     DELETE FROM ir_model_data
    #           WHERE model IN ('account.fiscal.position.tax.template',
    #                           'account.fiscal.position.account.template',
    #                           'account.fiscal.position.template',
    #                           'account.tax.template',
    #                           'account.account.template')
    # """)

    # Remove bad taxes from default values
    cr.execute(
        """
        SELECT v.id,
               v.value,
               f.ttype
          FROM ir_values v
          JOIN ir_model_fields f
            ON v.name = f.name
           AND v.model = f.model
         WHERE f.relation = 'account.tax'
           AND f.ttype IN ('many2many', 'many2one')
    """
    )
    defaults = cr.fetchall()
    ids_to_delete = []
    for id, value, ttype in defaults:
        pickled_value = pickle.loads(value)
        if pickled_value is False:
            continue
        if ttype == "many2one":
            if type(pickled_value) is not int or pickled_value in bad_tax_ids:
                ids_to_delete.append(id)
        else:
            filtered_values = (set(pickled_value) - bad_tax_ids) if type(pickled_value) is list else None
            if not filtered_values:
                ids_to_delete.append(id)
            elif len(filtered_values) != len(pickled_value):
                filtered_pickle = pickle.dumps(list(filtered_values))
                cr.execute("UPDATE ir_values SET value = %s WHERE id = %s", [filtered_pickle, id])

    if ids_to_delete:
        cr.execute("DELETE FROM ir_values WHERE id IN %s", [tuple(ids_to_delete)])
        _logger.info("Deleted default values using unusable taxes %s", ids_to_delete)
