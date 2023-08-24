# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "hr_contract", "has_bicycle", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE hr_contract c
           SET has_bicycle = true
          FROM hr_employee e
         WHERE e.contract_id = c.id
           AND e.has_bicycle
           AND c.active = true
        """,
        table="hr_contract",
        alias="c",
    )
    util.remove_field(cr, "hr.employee", "has_bicycle")
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.hr_leave_{stress,mandatory}_day_be"))

    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_pfi")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_cdi")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_cdd")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_cip")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_replacement")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.l10n_be_contract_type_clearly_defined_work")

    util.rename_field(cr, "l10n_be.281_10", "reference_year", "year")
    util.rename_field(cr, "l10n_be.281_45", "reference_year", "year")

    util.remove_model(cr, "l10n_be.individual.account.line", drop_table=False)
    util.remove_model(cr, "l10n_be.281_10.line", drop_table=False)
    util.remove_model(cr, "l10n_be.281_45.line", drop_table=False)
    util.remove_model(cr, "report.l10n_be_hr_payroll.report_281_10")
    util.remove_model(cr, "report.l10n_be_hr_payroll.report_281_45")
    util.remove_model(cr, "report.l10n_be_hr_payroll.report_individual_account")
