# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        account.view_company_inherit_form
        auth_ldap.company_form_view
        hr_timesheet_sheet.hr_timesheet_sheet_company
        l10n_fr_payroll.res_company_form_l0n_fr_payroll
        mrp.mrp_company
        pad.view_company_form_inherit_pad
        pad.view_company_form_with_pad          # for database < saas-12
        procurement.mrp_company
        project.task_company
        purchase.mrp_company
        report.reporting_settings_form_inherited
        sale.view_company_inherited_form2
        sale_stock.view_company_form_inherited_sale_stock
    """)

    for view in views:
        util.remove_view(cr, view)

    # TODO if there are any custom view that are hooking on `account_grp`,
    #      create a custom inherited view that reinstate it.
