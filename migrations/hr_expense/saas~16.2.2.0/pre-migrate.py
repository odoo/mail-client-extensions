# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense_sheet", "employee_journal_id", "int4")
    util.create_column(cr, "hr_expense_sheet", "payment_method_line_id", "int4")

    util.explode_execute(cr, "UPDATE hr_expense_sheet SET employee_journal_id = journal_id", table="hr_expense_sheet")
    cr.execute(
        """
            WITH prefered AS (
                SELECT j.company_id, (array_agg(l.id ORDER BY l.sequence, l.id))[1] as line_id
                  FROM account_payment_method_line l
                  JOIN account_journal j
                    ON j.id = l.journal_id
                  JOIN account_payment_method m
                    ON m.id = l.payment_method_id
                 WHERE m.payment_type = 'outbound'
              GROUP BY j.company_id
            )
            UPDATE hr_expense_sheet s
               SET payment_method_line_id = p.line_id
              FROM prefered p
             WHERE p.company_id = s.company_id
        """
    )

    util.remove_field(cr, "hr.expense.sheet", "bank_journal_id")
    util.remove_field(cr, "hr.expense.sheet", "attachment_number")

    util.remove_field(cr, "res.config.settings", "company_expense_journal_id")

    util.remove_field(cr, "res.company", "company_expense_journal_id")

    util.remove_field(cr, "hr.expense.refuse.wizard", "hr_expense_sheet_id")
    util.remove_field(cr, "hr.expense.refuse.wizard", "hr_expense_ids")

    util.remove_field(cr, "hr.expense", "is_refused")

    util.if_unchanged(cr, "hr_expense.hr_expense_template_refuse_reason", util.update_record_from_xml)
