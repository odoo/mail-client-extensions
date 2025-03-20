from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO account_payment_term_line(payment_id, value, value_amount, days, months, end_month)
             SELECT t.id, 'balance', 0.0, 0, 0, false
               FROM account_payment_term t
          LEFT JOIN account_payment_term_line l
                 ON l.payment_id = t.id
              WHERE l.id IS NULL
        """
    )
    # Migrate the carryover lines.
    cr.execute(
        """
        INSERT INTO account_report_external_value (
            name,
            value,
            date,
            target_report_expression_id,
            company_id,
            foreign_vat_fiscal_position_id,
            carryover_origin_expression_label,
            carryover_origin_report_line_id
        )
        SELECT
            tcl.name,
            SUM(tcl.amount) OVER (PARTITION BY tcl.tax_report_line_id ORDER BY tcl.date),
            tcl.date,
            carryover_expression_target.id,
            tcl.company_id,
            tcl.foreign_vat_fiscal_position_id,
            carryover_expression_origin.label,
            carryover_expression_origin.report_line_id
        FROM account_tax_carryover_line tcl
        JOIN account_tax_report_line trl ON trl.id = tcl.tax_report_line_id
        JOIN account_tax_report tr ON tr.id = trl.report_id
        JOIN account_report_expression expression ON expression.formula = trl.tag_name
        JOIN account_report_line new_trl ON new_trl.id = expression.report_line_id
        JOIN account_report new_tr ON
            new_tr.id = new_trl.report_id
            AND new_tr.country_id = tr.country_id
        JOIN account_report_expression carryover_expression_origin ON
            carryover_expression_origin.report_line_id = new_trl.id
            AND carryover_expression_origin.label = '_carryover_balance'
        JOIN account_report_expression carryover_expression_target ON
            carryover_expression_target.report_line_id = new_trl.id
            AND carryover_expression_target.label = '_applied_carryover_balance'
    """
    )

    # Cleanup.
    for table in (
        "account_tax_carryover_line",
        "account_tax_report_line",
        "account_tax_report",
        "account_tax_report_line_tags_rel_backup",
    ):
        cr.execute(util.format_query(cr, "DROP TABLE {} CASCADE", table))
