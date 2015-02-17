# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.remove_module(cr, 'base_report_designer')
    util.remove_module(cr, 'crm_mass_mailing')
    util.remove_module(cr, 'crm_profiling')     # FIXME convert to a survey?
    util.remove_module(cr, 'portal_claim')
    util.remove_module(cr, 'portal_project_issue')
    util.remove_module(cr, 'web_graph')
    util.remove_module(cr, 'website_instantclick')

    util.remove_module_deps(cr, 'mass_mailing', ('web_kanban_sparkline',))
    util.remove_module_deps(cr, 'sales_team', ('web_kanban_sparkline',))

    util.remove_module_deps(cr, 'project_timesheet', ('hr_timesheet_sheet',))
    util.new_module_dep(cr, 'project_timesheet', 'hr_timesheet')

    util.new_module(cr, 'account_bank_statement_import')
    util.new_module_dep(cr, 'account_bank_statement_import', 'account')
    util.new_module(cr, 'account_bank_statement_import_ofx')
    util.new_module_dep(cr, 'account_bank_statement_import_ofx', 'account_bank_statement_import')
    util.new_module(cr, 'account_bank_statement_import_qif')
    util.new_module_dep(cr, 'account_bank_statement_import_qif', 'account_bank_statement_import')
    util.new_module_dep(cr, 'l10n_be_coda', 'account_bank_statement_import')

    util.new_module(cr, 'barcodes')
    util.new_module_dep(cr, 'barcodes', 'web')
    util.new_module_dep(cr, 'point_of_sale', 'barcodes')
    util.new_module_dep(cr, 'stock', 'barcodes')

    util.merge_module(cr, 'email_template', 'mail')

    util.new_module(cr, 'theme_bootswatch')
    util.new_module_dep(cr, 'theme_bootswatch', 'website')
    cr.execute("""SELECT 1
                    FROM ir_ui_view v
                    JOIN ir_model_data d ON (d.model='ir.ui.view' AND v.id=d.res_id)
                   WHERE d.module='website'
                     AND d.name IN ('theme_amelia', 'theme_cerulean', 'theme_cosmo',
                                    'theme_cyborg', 'theme_flatly', 'theme_journal',
                                    'theme_readable', 'theme_simplex', 'theme_slate',
                                    'theme_spacelab', 'theme_united', 'theme_yeti')
                     AND v.active=true
               """)
    if cr.rowcount:
        util.force_install_module(cr, 'theme_bootswatch')

    util.new_module(cr, 'website_links')
    util.new_module_dep(cr, 'mass_mailing', 'website_links')

    util.new_module(cr, 'web_tip')
    util.new_module_dep(cr, 'web_tip', 'web')
    for m in 'account crm event hr project purchase website_quote'.split():
        util.new_module_dep(cr, m, 'web_tip')

    util.new_module(cr, 'mail_tip', auto_install_deps=('mail', 'web_tip'))
