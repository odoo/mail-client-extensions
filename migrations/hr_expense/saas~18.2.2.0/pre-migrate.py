from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # Removing expense sheet records (as we don't just remove_model)
    util.remove_record(cr, "hr_expense.ir_rule_hr_expense_sheet_manager")
    util.remove_record(cr, "hr_expense.ir_rule_hr_expense_sheet_approver")
    util.remove_record(cr, "hr_expense.ir_rule_hr_expense_sheet_employee")
    util.remove_record(cr, "hr_expense.ir_rule_hr_expense_sheet_employee_not_draft")
    util.remove_record(cr, "hr_expense.hr_expense_report_comp_rule")
    util.remove_view(cr, "hr_expense.hr_expense_sheet_view_activity")
    util.remove_view(cr, "hr_expense.hr_expense_sheet_view_search")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_graph")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_pivot")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_kanban_header")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_kanban_no_header")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_kanban")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_form")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_dashboard_tree_header")
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_tree")

    util.create_column(cr, "hr_expense", "account_move_id", "integer")
    util.create_column(cr, "hr_expense", "department_id", "integer")
    util.create_column(cr, "hr_expense", "manager_id", "integer")
    util.create_column(cr, "hr_expense", "former_sheet_id", "integer")
    util.create_column(cr, "hr_expense", "payment_method_line_id", "integer")
    util.create_column(cr, "hr_expense", "approval_date", "timestamp")
    util.create_column(cr, "hr_expense", "untaxed_amount", "numeric")
    util.create_column(cr, "hr_expense", "approval_state", "varchar")

    util.explode_execute(
        cr,
        """
          WITH new_values AS (
               SELECT expense.id AS expense_id,
                      sheet.id AS former_sheet_id,
                      ROUND((expense.total_amount - expense.tax_amount)::numeric, COALESCE(currency.rounding, company_currency.rounding, 2)::int) AS untaxed_amount,
                      sheet.user_id AS manager_id,
                      sheet.approval_date AS approval_date,
                      CASE WHEN sheet.approval_state IS NULL THEN NULL
                           WHEN sheet.approval_state = 'submit' THEN 'submitted'
                           WHEN sheet.approval_state = 'approve' THEN 'approved'
                      ELSE 'refused'  -- WHEN 'cancel'
                      END AS approval_state, -- States were renamed for more consistency
                      sheet.payment_method_line_id AS payment_method_line_id,
                      employee.department_id AS department_id,
                      move_line.move_id AS move_id  -- Because it's more reliable than the expense_sheet_id on the move
                 FROM hr_expense AS expense
                 JOIN hr_expense_sheet AS sheet
                   ON expense.sheet_id = sheet.id
                 JOIN res_company AS company
                   ON expense.company_id = company.id
                 JOIN hr_employee AS employee
                   ON expense.employee_id = employee.id
                 JOIN res_currency AS company_currency
                   ON company.currency_id = company_currency.id
            LEFT JOIN res_currency AS currency
                   ON expense.currency_id = currency.id
            LEFT JOIN account_move_line AS move_line
                   ON move_line.expense_id = expense.id
                WHERE {parallel_filter}
        )
        UPDATE hr_expense
           SET manager_id = new_values.manager_id,
               former_sheet_id = new_values.former_sheet_id,
               approval_date = new_values.approval_date,
               approval_state = new_values.approval_state,
               payment_method_line_id = new_values.payment_method_line_id,
               department_id = new_values.department_id,
               account_move_id = new_values.move_id,
               untaxed_amount = new_values.untaxed_amount
         FROM new_values
        WHERE hr_expense.id = new_values.expense_id
        """,
        "hr_expense",
        alias="expense",
    )

    cr.execute("""
        SELECT former_sheet_id, max(id)
          FROM hr_expense
         WHERE former_sheet_id IS NOT NULL  -- is it possible?
      GROUP BY former_sheet_id
    """)
    sheet_mapping = dict(cr.fetchall())
    if sheet_mapping:
        util.replace_record_references_batch(cr, sheet_mapping, model_src="hr.expense.sheet", model_dst="hr.expense")

    util.remove_field(cr, "account.move", "show_commercial_partner_warning")
    util.remove_field(cr, "hr.expense", "approved_by")
    util.remove_field(cr, "hr.expense", "approved_on")
    util.remove_field(cr, "hr.expense", "accounting_date")

    util.remove_field(cr, "account.move", "expense_sheet_id")
    util.remove_field(cr, "account.payment", "expense_sheet_id")
    util.remove_field(cr, "hr.expense.approve.duplicate", "sheet_ids")
    util.remove_field(cr, "hr.expense.refuse.wizard", "sheet_ids")
    util.remove_field(cr, "hr.expense", "sheet_id")

    util.rename_field(cr, "hr.department", "expense_sheets_to_approve_count", "expenses_to_approve_count")
    util.rename_xmlid(cr, *eb("hr_expense.report_expense{_sheet,}_img"))
    util.rename_xmlid(cr, *eb("hr_expense.report_expense{_sheet,}"))
    util.rename_xmlid(cr, *eb("hr_expense.action_report_hr_expense{_sheet,}"))
    util.rename_xmlid(cr, *eb("hr_expense.action_report_expense{_sheet,}_img"))
    util.rename_xmlid(cr, *eb("hr_expense.hr_expense{_sheet,}_view_search_with_panel"))
