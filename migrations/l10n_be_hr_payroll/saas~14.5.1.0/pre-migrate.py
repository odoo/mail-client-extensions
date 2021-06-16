# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.payslip", "has_attachment_salary")
    util.remove_field(cr, "hr.contract", "attachment_salary_ids")
    util.remove_field(cr, "hr.contract.history", "attachment_salary_ids")

    util.remove_view(cr, "l10n_be_hr_payroll.ll10n_be_attachment_salary_report_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_attachment_salary_report_view_pivot")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_tree")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_form")

    util.remove_record(cr, "l10n_be_hr_payroll.ir_rule_attachment_salary_report_multi_company")

    util.remove_model(cr, "l10n_be.attachment.salary")
    util.remove_model(cr, "l10n_be.attachment.salary.report")

    util.create_column(cr, "hr_employee", "l10n_be_dependent_children_attachment", "int4")
