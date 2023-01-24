# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.expense.sheet", "bank_journal_id")
    util.remove_field(cr, "hr.expense.sheet", "attachment_number")

    util.remove_field(cr, "res.config.settings", "company_expense_journal_id")

    util.remove_field(cr, "res.company", "company_expense_journal_id")

    util.remove_field(cr, "hr.expense.refuse.wizard", "hr_expense_sheet_id")
    util.remove_field(cr, "hr.expense.refuse.wizard", "hr_expense_ids")

    util.remove_field(cr, "hr.expense", "is_refused")

    util.if_unchanged(cr, "hr_expense.hr_expense_template_refuse_reason", util.update_record_from_xml)
