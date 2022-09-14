# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    if not util.has_enterprise():
        modules = [mod for mod in [
            'account_analytic_analysis',
            'account_report_followup',
            'hr_evaluation',        # replaced by hr_appraisal
            'l10n_be_coda',

            # new saas-6 modules moved to enterprise.
            'account_bank_statement_import_ofx',
            'account_bank_statement_import_qif',
            'inter_company_rules',
            'pos_loyalty',
            'website_crm_score',
            'website_version',
        ] if util.module_installed(cr, mod)]
        if modules:
            # XXX specific exception?
            raise util.MigrationError('Enterprise needed for %s' % ', '.join(modules))

    util.rename_module(cr, 'account_analytic_analysis', 'sale_contract')
    util.rename_module(cr, 'account_followup', 'account_reports_followup')
    util.rename_module(cr, 'hr_evaluation', 'hr_appraisal')
    util.rename_module(cr, 'planner', 'web_planner')
    util.rename_module(cr, 'website_mail_group', 'website_mail_channel')

    util.merge_module(cr, "im_chat", "mail")

    # keep some tables used by other migration scripts
    if not util.modules_installed(cr, "sale_contract"):
        util.remove_module(cr, "hr_timesheet_invoice")

    util.new_module_dep(cr, 'base_iban', 'account')  # we can leave the 'base' dep

    no_more_board = 'account crm event fleet google_drive hr project stock'.split()
    for m in no_more_board:
        util.remove_module_deps(cr, m, ('board',))

    util.new_module_dep(cr, 'account', 'web_planner')

    util.new_module(cr, "account_tax_cash_basis", deps={"account"})
    util.new_module(cr, "account_cash_basis_base_account", deps={"account_tax_cash_basis"}, auto_install=True)
    util.new_module(cr, "account_lock", deps={"account"})

    util.new_module(cr, 'account_check_printing', deps=('account',),
                    auto_install=util.modules_installed(cr, 'account_check_writing'))

    util.new_module(cr, 'account_full_reconcile', deps=('account',), auto_install=True)

    util.new_module(cr, 'account_extra_reports', deps=('account_accountant',), auto_install=True)
    util.force_migration_of_fresh_module(cr, 'account_extra_reports')

    util.new_module_dep(cr, 'crm', 'web_planner')  # TODO move data from delete module planner_crm

    util.remove_module_deps(cr, 'event_sale', ('sale_crm',))
    util.new_module_dep(cr, 'event_sale', 'sale')

    util.new_module_dep(cr, 'hr', 'web_kanban')
    util.new_module_dep(cr, 'hr_expense', 'hr_contract')
    util.new_module_dep(cr, 'hr_recruitment', 'document')
    util.new_module_dep(cr, 'im_odoo_support', 'mail')

    # These modules had only a dep on `account_chart` which is now gone.
    # Replace with a dep on `account`
    l10n = 'ar bo cl jp pa pe th'.split()
    for m in l10n:
        util.new_module_dep(cr, 'l10n_' + m, 'account')

    util.new_module(cr, "l10n_au", deps={"account"})
    util.new_module(cr, "l10n_de_skr03", deps={"l10n_de"})
    util.new_module(cr, "l10n_de_skr04", deps={"l10n_de"})

    util.new_module(cr, "l10n_in_schedule6", deps={"account"})

    util.new_module_dep(cr, 'l10n_ca', 'report')
    util.new_module_dep(cr, 'l10n_ca', 'l10n_multilang')
    util.new_module_dep(cr, 'l10n_us', 'report')

    util.new_module(cr, 'l10n_generic_coa')
    util.new_module_dep(cr, 'l10n_generic_coa', 'account')
    util.new_module_dep(cr, 'l10n_us', 'l10n_generic_coa')

    util.new_module(cr, 'l10n_fr_certification', deps={'l10n_fr'})
    util.new_module(cr, 'l10n_fr_sale_closing', deps={'l10n_fr_certification'}, auto_install=True)
    util.new_module(cr, 'l10n_fr_pos_cert', deps={'l10n_fr_sale_closing', 'point_of_sale'})

    util.new_module_dep(cr, 'lunch', 'web')
    util.new_module_dep(cr, 'lunch', 'decimal_precision')
    util.remove_module_deps(cr, 'lunch', ('report',))

    util.new_module(cr, 'link_tracker')
    util.new_module_dep(cr, 'link_tracker', 'marketing')
    util.new_module_dep(cr, 'link_tracker', 'utm')

    util.new_module(cr, 'web_editor', deps=('web',), auto_install=True)

    util.new_module_dep(cr, 'mail', 'bus')

    util.remove_module_deps(cr, 'mass_mailing', ('website_mail', 'website_links'))
    util.new_module_dep(cr, 'mass_mailing', 'link_tracker')
    util.new_module_dep(cr, 'mass_mailing', 'web_editor')

    util.new_module_dep(cr, 'mrp_repair', 'stock')
    util.remove_module_deps(cr, 'mrp_repair', ('mrp',))

    util.remove_module_deps(cr, 'procurement_jit', ('procurement', 'stock'))
    util.new_module_dep(cr, 'procurement_jit', 'sale_stock')

    util.new_module(cr, 'product_uos')
    util.new_module_dep(cr, 'product_uos', 'sale')
    if util.module_installed(cr, 'sale'):
        cr.execute("SELECT count(1) FROM product_template WHERE uos_id IS NOT NULL AND uos_id != uom_id")
        if cr.fetchone()[0]:
            util.force_install_module(cr, 'product_uos')

    util.new_module_dep(cr, 'project', 'portal')
    util.new_module_dep(cr, 'project', 'web_planner')

    util.remove_module_deps(cr, 'project_timesheet',
                            ('hr_timesheet', 'sale_contract', 'procurement'))
    util.new_module_dep(cr, 'project_issue_sheet', 'project_timesheet')

    util.new_module_dep(cr, 'report_intrastat', 'delivery')

    util.remove_module_deps(cr, 'sale', ('account_voucher',))
    util.new_module_dep(cr, 'sale', 'account')

    util.remove_module_deps(cr, 'sale_service', ('procurement', 'procurement_jit'))
    util.new_module_dep(cr, 'sale_service', 'project_timesheet')

    util.new_module(cr, 'sale_timesheet', deps=('sale', 'hr_timesheet'), auto_install=True)
    util.new_module_dep(cr, 'project_timesheet', 'sale_timesheet')
    util.new_module_dep(cr, 'sale_service', 'sale_timesheet')

    util.remove_module_deps(cr, 'stock', ('web_kanban_gauge',))
    util.new_module_dep(cr, 'stock', 'barcodes')
    util.new_module_dep(cr, 'stock', 'web_planner')

    util.new_module_dep(cr, 'stock_landed_costs', 'purchase')

    util.new_module(cr, 'web_settings_dashboard')
    util.new_module_dep(cr, 'web_settings_dashboard', 'web_planner')
    util.force_install_module(cr, 'web_planner')
    util.force_install_module(cr, 'web_settings_dashboard')

    util.new_module_dep(cr, 'website', 'web_editor')
    util.new_module_dep(cr, 'website', 'web_planner')
    util.remove_module_deps(cr, 'website', ('mail',))

    util.new_module(cr, 'website_theme_install', deps=('website',), auto_install=True)

    util.new_module(cr, 'website_form')
    util.new_module_dep(cr, 'website_form', 'website')
    util.new_module_dep(cr, 'website_form', 'mail')

    util.new_module_dep(cr, 'website_crm', 'website_form')
    util.new_module_dep(cr, 'website_hr_recruitment', 'website_form')

    util.new_module_dep(cr, 'website_links', 'link_tracker')
    util.force_migration_of_fresh_module(cr, 'link_tracker')

    # in saas-6, the website part was directly in mass_mailing module
    # force `website` install if mass_mailing was installed to keep saas-6 behavior
    util.new_module(cr, 'website_mass_mailing', deps=('mass_mailing',), auto_install=True)
    util.new_module_dep(cr, 'website_mass_mailing', 'website')

    util.remove_module_deps(cr, 'website_portal', ('sale',))

    util.new_module(cr, 'website_portal_sale', deps=('website_portal', 'sale'), auto_install=True)
    util.new_module_dep(cr, 'website_portal_sale', 'website_payment')

    util.remove_module_deps(cr, 'website_project_issue', ('website', 'portal'))
    util.new_module_dep(cr, 'website_project_issue', 'website_portal')

    util.new_module(cr, 'website_project_issue_sheet',
                    deps=('website_project_issue', 'project_issue_sheet'),
                    auto_install=True)

    util.remove_module_deps(cr, 'website_quote', ('website_portal',))   # still indirect
    util.new_module_dep(cr, 'website_quote', 'website_portal_sale')
    util.new_module_dep(cr, 'website_quote', 'website_mail')

    util.remove_module_deps(cr, 'website_sale', ('website_portal',))   # still indirect
    util.new_module_dep(cr, 'website_sale', 'website_portal_sale')
    util.new_module_dep(cr, 'website_sale', 'website_mail')
    util.new_module_dep(cr, 'website_sale', 'rating')

    util.new_module_dep(cr, 'website_slides', 'marketing')

    if util.has_enterprise():
        util.new_module(cr, 'account_tax_python')
        util.new_module_dep(cr, 'account_tax_python', 'account')
        if util.module_installed(cr, 'account') and util.table_exists(cr, "account_tax"):
            cr.execute("SELECT count(1) FROM account_tax WHERE type='code'")
            if cr.fetchone()[0]:
                util.force_install_module(cr, 'account_tax_python')
                util.force_migration_of_fresh_module(cr, 'account_tax_python')

        util.new_module(cr, 'account_reports', deps=('account',), auto_install=True)
        util.force_migration_of_fresh_module(cr, 'account_reports')
        util.new_module(cr, 'account_extension', deps=('account',), auto_install=True)

        l10n = 'au ar at be bo br ch cl co de_skr03 de_skr04 do es et fr gr hr hu in jp lu ma nl no pl ro sg si th uk uy vn'.split()
        for l in l10n:
            util.new_module(cr, 'l10n_' + l + '_reports', deps=('l10n_' + l, 'account_reports'),
                            auto_install=True)

        util.new_module(cr, 'currency_rate_live', deps=('account',), auto_install=True)

        util.new_module(cr, 'hr_holidays_gantt', deps=('hr_holidays', 'web_gantt'), auto_install=True)
        util.new_module(cr, 'mass_mailing_themes', deps=('mass_mailing',), auto_install=True)
        util.new_module(cr, 'website_enterprise', deps=('website',), auto_install=True)


    # some cleanup
    removed_modules = util.splitlines("""
        # salespocalypse
        account_analytic_plans
        analytic_contract_hr_expense
        analytic_user_function
        purchase_analytic_plans
        sale_analytic_plans
        sale_journal
        stock_invoice_directly

        # purchasocalypse
        purchase_double_validation

        # accountpocalypse
        # account_anglo_saxon
        account_bank_statement_extensions
        account_chart
        account_check_writing
        account_payment
        account_sequence
        multi_company

        # rest-pocalyspe
        auth_openid
        contacts
        edi
        hr_applicant_document       # feature move to hr_recruitment

        knowledge
        planner_crm
        portal_project
        share
        web_api
        web_kanban_sparkline
        web_linkedin
        web_tests
        web_tests_demo
        website_certification
        website_project
        website_report
    """)
    for m in removed_modules:
        util.remove_module(cr, m)
