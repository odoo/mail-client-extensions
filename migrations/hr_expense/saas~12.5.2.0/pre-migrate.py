# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_expense x
           SET company_id = e.company_id
          FROM hr_employee e
         WHERE e.id = x.employee_id
           AND x.company_id IS NULL
    """
    )

    util.rename_xmlid(cr, "hr_expense.view_hr_expense_filter", "hr_expense.hr_expense_view_search", noupdate=False)
    util.rename_xmlid(
        cr, "hr_expense.view_hr_expense_sheet_filter", "hr_expense.hr_expense_sheet_view_search", noupdate=False
    )

    util.create_column(cr, "hr_expense_sheet_register_payment_wizard", "expense_sheet_id", "int4")
    # as this new field is required, remove all records (this is wizard)
    cr.execute("DELETE FROM hr_expense_sheet_register_payment_wizard")
