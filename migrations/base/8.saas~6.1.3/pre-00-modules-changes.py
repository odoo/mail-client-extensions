# -*- coding: utf-8 -*-
from openerp import tools
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

    util.new_module_dep(cr, 'procurement_jit', 'stock')

    util.new_module(cr, 'rating')
    util.new_module_dep(cr, 'rating', 'mail')
    util.new_module_dep(cr, 'im_livechat', 'rating')

    util.merge_module(cr, 'email_template', 'mail')

    util.new_module(cr, 'theme_bootswatch')
    util.new_module_dep(cr, 'theme_bootswatch', 'website')
    themes = tuple("""theme_amelia theme_cerulean theme_cosmo
                      theme_cyborg theme_flatly theme_journal
                      theme_readable theme_simplex theme_slate
                      theme_spacelab theme_united theme_yeti
    """.split())
    cr.execute("""SELECT 1
                    FROM ir_ui_view v
                    JOIN ir_model_data d ON (d.model='ir.ui.view' AND v.id=d.res_id)
                   WHERE d.module='website'
                     AND d.name IN %s
                     AND v.active=true
               """, [themes])
    if cr.rowcount:
        util.force_install_module(cr, 'theme_bootswatch')
        for t in themes:
            util.rename_xmlid(cr, 'website.' + t, 'theme_bootswatch.' + t)

    util.new_module(cr, 'website_links')
    util.new_module_dep(cr, 'mass_mailing', 'website_links')

    util.new_module(cr, 'web_tip')
    util.new_module_dep(cr, 'web_tip', 'web')
    for m in 'account crm event hr project purchase website_quote'.split():
        util.new_module_dep(cr, m, 'web_tip')

    util.new_module(cr, 'mail_tip', auto_install_deps=('mail', 'web_tip'))

    util.new_module(cr, 'utm')
    util.new_module_dep(cr, 'utm', 'marketing')
    for m in 'crm hr_recruitment mass_mailing'.split():
        util.new_module_dep(cr, 'crm', 'utm')

    # `utm` module need a migration script to steal models from `crm` module
    # you may think this is clever hack, but I'm just an asshole that want the
    # migration script to be in a specific file instead of a method above...
    cr.execute("""UPDATE ir_module_module
                     SET state='to upgrade'
                   WHERE name='utm'
                     AND state='to install'
               RETURNING id""")
    if cr.rowcount:
        # force module in `init` mode beside its state is forced to `to upgrade`
        # see openerp/modules/loading.py:161 (in saas-6)
        tools.config['init']['utm'] = "oh yeah!"
