# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.new_module_dep(cr, 'auth_oauth', 'auth_signup')
    util.new_module_dep(cr, 'document', 'mail')
    util.new_module_dep(cr, 'hr_recruitment', 'web_kanban_gauge')
    util.new_module_dep(cr, 'website_mail', 'email_template')

    util.new_module(cr, 'report', auto_install_deps=('base',))
    for m in ['account', 'lunch', 'mrp', 'purchase', 'sale']:
        util.new_module_dep(cr, m, 'report')

    util.new_module(cr, 'website_report', auto_install_deps=('website', 'report'))

    util.new_module_dep(cr, 'survey', 'email_template')
    util.new_module_dep(cr, 'survey', 'website')
    util.new_module_dep(cr, 'survey', 'marketing')
    util.new_module(cr, 'survey_crm', auto_install_deps=('survey', 'crm'))
