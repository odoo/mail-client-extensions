# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Use config bar for real config steps (PR:70115)
    # ===============================================================

    util.remove_view(cr, "account.dashboard_onboarding_bill_step")
    util.create_column(cr, "res_company", "account_setup_taxes_state", "varchar", default="not_done")

    # ===============================================================
    # French tax report: carry over tax grid 27 to tax grid 22 (PR: (odoo) 69887 & (enterprise) 17953)
    # ===============================================================
    util.create_column(cr, "account_tax_report_line", "is_carryover_persistent", "bool", default=True)
    util.create_column(cr, "account_tax_report_line", "is_carryover_used_in_balance", "bool")

    # ===============================================================
    # Tax details per move line (PR:70866 & PR:18344)
    # ===============================================================

    util.create_column(cr, "account_move_line", "group_tax_id", "int4")

    query = """
        UPDATE account_move_line tax_line
           SET group_tax_id = r.parent_tax
          FROM account_tax tax
          JOIN account_tax_filiation_rel r ON r.child_tax = tax.id
         WHERE tax_line.tax_line_id = tax.id
           AND tax.type_tax_use = 'none'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line"))

    # ===============================================================
    # Add category to analytic account line (PR: (odoo) 68708 & (enterprise) 18594)
    # ===============================================================

    cr.execute(
        """
            UPDATE account_analytic_line
               SET category = CASE
                                WHEN am.move_type IN ('out_invoice', 'out_refund') THEN 'invoice'
                                WHEN am.move_type IN ('in_invoice', 'in_refund') THEN 'vendor_bill'
                              END
              FROM account_analytic_line aal
                   JOIN account_move_line aml
                     ON aal.move_id = aml.id
                   JOIN account_move am
                     ON aml.move_id = am.id
             WHERE account_analytic_line.id = aal.id
        """
    )

    # ==========================================================================
    # The Reconciliation Models usability imp (PR: odoo#73043, enterprise#19395)
    # ==========================================================================

    util.rename_field(cr, 'account.reconcile.model.line', 'match_total_amount', 'allow_payment_tolerance')
    util.rename_field(cr, 'account.reconcile.model.line', 'match_total_amount_param', 'payment_tolerance_param')

    for model_name in ('account.reconcile.model', 'account.reconcile.model.template'):
        table_name = util.table_of_model(cr, model_name)
        util.rename_field(cr, model_name, 'match_total_amount', 'allow_payment_tolerance')
        util.rename_field(cr, model_name, 'match_total_amount_param', 'payment_tolerance_param')
        util.create_column(cr, table_name, 'payment_tolerance_type', 'varchar', default='percentage')

        cr.execute(f'''
            UPDATE {table_name}
            SET payment_tolerance_param = 100 - payment_tolerance_param
        ''')
