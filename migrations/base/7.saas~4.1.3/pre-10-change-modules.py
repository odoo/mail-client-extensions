# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.remove_module(cr, 'idea')
    util.remove_module(cr, 'crm_todo')
    util.remove_module(cr, 'auth_oauth_signup')

    util.new_module_dep(cr, 'auth_oauth', 'auth_signup')
    util.new_module_dep(cr, 'document', 'mail')
    util.new_module_dep(cr, 'hr_recruitment', 'web_kanban_gauge')
    util.new_module_dep(cr, 'website_mail', 'email_template')

    util.new_module(cr, 'report', auto_install_deps=('base',))
    reports_modules = """
        account
        hr_attendance
        hr_expense
        hr_payroll
        hr_timesheet_invoice
        lunch
        mrp
        purchase
        sale
    """.split()
    for m in reports_modules:
        util.new_module_dep(cr, m, 'report')

    util.new_module(cr, 'website_report', auto_install_deps=('website', 'report'))

    util.new_module_dep(cr, 'survey', 'email_template')
    util.new_module_dep(cr, 'survey', 'website')
    util.new_module_dep(cr, 'survey', 'marketing')
    util.new_module(cr, 'survey_crm', auto_install_deps=('survey', 'crm'))

    # marketing module is splitted with marketing_crm module
    # if users have marketing, they need marketing_crm
    cr.execute("""UPDATE ir_model_data
                     SET module=%s
                   WHERE module=%s
                     AND name in %s
               """, ('marketing_crm', 'marketing', ('view_crm_lead_form', 'view_crm_opportunity_form')))

    util.remove_module_deps(cr, 'markering', ('crm',))
    util.new_module(cr, 'marketing_crm', ('marketing', 'crm'))

    util.new_module_dep(cr, 'mass_mailing', 'marketing')
    util.new_module_dep(cr, 'mass_mailing', 'website_mail')
