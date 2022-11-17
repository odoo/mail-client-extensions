# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_lu_reports.view_l10n_lu_generate_tax_report")
    util.remove_view(cr, "l10n_lu_reports.view_l10n_lu_yearly_tax_report_manual_export")
    util.remove_view(cr, "l10n_lu_reports.view_l10n_lu_yearly_tax_report_manual_extended")
    if util.table_exists(cr, "l10n_lu_reports_annual_vat_report_appendix_expenditures"):
        util.rename_model(
            cr,
            "l10n_lu_reports_annual_vat.report.appendix.expenditures",
            "l10n_lu_reports.report.appendix.expenditures",
        )

    util.remove_constraint(cr, "l10n_lu_yearly_tax_report_manual", "l10n_lu_yearly_tax_report_manual_year_unique")
    if not util.table_exists(cr, "l10n_lu_yearly_tax_report_manual_res_company_rel"):
        util.create_m2m(
            cr, "l10n_lu_yearly_tax_report_manual_res_company_rel", "l10n_lu_yearly_tax_report_manual", "res_company"
        )
        cr.execute(
            """
            INSERT INTO l10n_lu_yearly_tax_report_manual_res_company_rel (
                l10n_lu_yearly_tax_report_manual_id,
                res_company_id
            )
            SELECT id, company_id
            FROM l10n_lu_yearly_tax_report_manual;
            """
        )
    util.remove_field(cr, "l10n_lu.yearly.tax.report.manual", "company_id")
