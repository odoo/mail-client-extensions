from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense", "payslip_id", "integer")
    util.create_column(cr, "hr_expense", "refund_in_payslip", "boolean")
    util.remove_view(cr, "hr_payroll_expense.hr_expense_sheet_view_form_inherit_payroll")
    util.remove_field(cr, "hr.payslip", "expense_sheet_ids")

    if util.table_exists(cr, "hr_expense_sheet"):
        util.explode_execute(
            cr,
            """
                UPDATE hr_expense
                   SET payslip_id = hr_expense_sheet.payslip_id,
                       refund_in_payslip = hr_expense_sheet.refund_in_payslip
                  FROM hr_expense_sheet
                 WHERE hr_expense.former_sheet_id = hr_expense_sheet.id
            """,
            "hr_expense",
        )
