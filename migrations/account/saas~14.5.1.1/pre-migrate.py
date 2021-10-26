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
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", prefix="tax_line."))

    # ===============================================================
    # Add category to analytic account line (PR: (odoo) 68708 & (enterprise) 18594)
    # ===============================================================

    queries = [
        """
            UPDATE account_analytic_line aal
               SET category = 'invoice'
              FROM account_move_line aml
              JOIN account_move am ON aml.move_id = am.id
             WHERE aal.move_id = aml.id
               AND am.move_type IN ('out_invoice', 'out_refund')
        """,
        """
            UPDATE account_analytic_line aal
               SET category = 'vendor_bill'
              FROM account_move_line aml
              JOIN account_move am ON aml.move_id = am.id
             WHERE aal.move_id = aml.id
               AND am.move_type IN ('in_invoice', 'in_refund')
        """,
    ]
    for query in queries:
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", prefix="aal."))

    # ==========================================================================
    # The Reconciliation Models usability imp (PR: odoo#73043, enterprise#19395)
    # ==========================================================================

    util.rename_field(cr, "account.reconcile.model.line", "match_total_amount", "allow_payment_tolerance")
    util.rename_field(cr, "account.reconcile.model.line", "match_total_amount_param", "payment_tolerance_param")

    for model_name in ("account.reconcile.model", "account.reconcile.model.template"):
        table_name = util.table_of_model(cr, model_name)
        util.rename_field(cr, model_name, "match_total_amount", "allow_payment_tolerance")
        util.rename_field(cr, model_name, "match_total_amount_param", "payment_tolerance_param")
        util.create_column(cr, table_name, "payment_tolerance_type", "varchar", default="percentage")

        cr.execute(f"UPDATE {table_name} SET payment_tolerance_param = 100 - payment_tolerance_param")

    # ===============================================================
    # tax_exigible on account.move.line removal + preceding_subtotal on tax groups (PR: odoo#74138, enterprise#19802)
    # ===============================================================

    util.rename_field(cr, "account.move", "tax_cash_basis_move_id", "tax_cash_basis_origin_move_id")

    util.create_column(cr, "account_move", "always_tax_exigible", "boolean")
    util.create_column(cr, "account_tax_group", "preceding_subtotal", "varchar")

    # Delete the tags from non-exigible move lines; they were not used by reports, and we now
    # only display them on cash basis moves.
    query_tags = """
        DELETE
        FROM account_account_tag_account_move_line_rel aml_tag
        USING account_move_line aml
        WHERE aml_tag.account_move_line_id = aml.id
        AND NOT aml.tax_exigible
        AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query_tags, table="account_move_line", prefix="aml."))

    # Since we removed the tags, tax_audit needs to be reset for those lines.
    query_tax_audit = """
        UPDATE account_move_line
        SET tax_audit = ''
        WHERE NOT tax_exigible
        AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query_tax_audit, table="account_move_line"))

    # Set always_tax_exigible: it will be true on all misc entries without any non-exigible line
    query_always_exigible = """
        WITH cte AS (
            SELECT m.id
            FROM account_move m
            LEFT JOIN account_move_line l ON l.move_id = m.id
            WHERE m.move_type = 'entry'
            AND {parallel_filter}
            GROUP BY m.id
            HAVING bool_and(l.tax_exigible) is not false
        )

        UPDATE account_move m
        SET always_tax_exigible = true
        FROM cte
        WHERE cte.id = m.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query_always_exigible, table="account_move", prefix="m."))

    util.remove_field(cr, "account.move", "amount_by_group")
    util.remove_field(cr, "account.move.line", "tax_exigible")

    # ===============================================================
    # OSS report (PR: (odoo) 73602 & (enterprise) 19628)
    # ===============================================================

    util.rename_field(cr, "res.config.settings", "module_l10n_eu_service", "module_l10n_eu_oss")
    util.create_m2m(cr, "account_account_tag_product_template_rel", "product_template", "account_account_tag")

    # =================================================================
    # Import First Bill Modal Improvement (PR: odoo#75815)
    # =================================================================

    util.remove_field(cr, "account.tour.upload.bill", "sample_bill_preview")
