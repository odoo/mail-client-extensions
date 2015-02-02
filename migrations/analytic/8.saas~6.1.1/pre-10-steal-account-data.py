# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # TODO remove project.account.analytic.line model and view/action in a `account` script

    models = util.splitlines("""
        ## models
        account.analytic.journal

        ## wizards
        account.analytic.balance
        account.analytic.chart
        account.analytic.cost.ledger.journal.report
        account.analytic.cost.ledger
        account.analytic.inverted.balance
        account.analytic.journal.report
    """)
    for m in models:
        util.move_model(cr, m, 'account', 'analytic', move_data=True)

    reports = util.splitlines("""
        report.account.report_analyticbalance
        report.account.report_analyticjournal
        report.account.report_analyticcostledger
        report.account.report_invertedanalyticbalance
        report.account.report_analyticcostledgerquantity
    """)
    for r in reports:
        # FIXME check ...
        util.move_model(cr, r, 'account', 'analytic', move_data=True)

    xids = util.splitlines("""
        ## whole file `{project,analytic}_demo.xml` moved from `account` module
        cose_journal_sale
        sit

        ## whole file `analytic_account_demo.xml` moved from `account` module
        analytic_root
        analytic_absences
        analytic_internal
        analytic_our_super_product
        analytic_project_1
        analytic_project_2
        analytic_journal_trainings
        analytic_in_house
        analytic_online
        analytic_support
        analytic_partners
        analytic_customers
        analytic_support_internal
        analytic_integration
        analytic_consultancy
        analytic_super_product_trainings
        analytic_seagate_p1
        analytic_seagate_p2
        analytic_millennium_industries
        analytic_integration_c2c
        analytic_agrolait
        analytic_asustek
        analytic_deltapc
        analytic_spark
        analytic_nebula
        analytic_luminous_technologies
        analytic_desertic_hispafuentes
        analytic_think_big_systems
        analytic_partners_camp_to_camp
        analytic_project_2_support
        analytic_project_2_development
        analytic_project_1_trainings
        analytic_project_1_development
        analytic_administratif
        analytic_commercial_marketing
        analytic_our_super_product_development
        analytic_stable
        analytic_trunk
        analytic_paid
        analytic_unpaid

        ## actions + bindings
        account_account_analytic_account_form
        act_account_renew_view
        action_account_analytic_account_tree2
        action_account_analytic_line_form
        action_account_tree1
        ir_open_account_analytic_account
        action_account_analytic_account_line_extended_form
        action_account_analytic_journal_form
        action_account_analytic_journal_open_form
        action_account_analytic_chart
        action_account_analytic_balance
        account_analytic_balance_values
        action_account_analytic_cost_ledger_journal
        account_analytic_cost_ledger_journal_values
        action_account_analytic_cost
        account_analytic_cost_values
        action_account_analytic_invert_balance
        account_analytic_invert_balance_values
        action_account_analytic_journal
        account_analytic_journal_values

        ## menus
        account_analytic_def_account
        account_def_analytic_journal

        ## views
        view_account_analytic_account_list
        view_account_analytic_account_search
        view_account_analytic_account_tree
        view_account_analytic_line_form
        view_account_analytic_line_tree
        view_account_analytic_line_filter
        account_analytic_line_extended_form
        view_account_analytic_journal_tree
        view_analytic_journal_search
        view_account_analytic_journal_form
        account_analytic_chart_view
        account_analytic_balance_view
        account_analytic_cost_ledger_journal_view
        account_analytic_cost_view
        account_analytic_invert_balance_view
        account_analytic_journal_view

        ## reports
        report_analyticbalance
        report_analyticcostledger
        report_analyticcostledgerquantity
        report_analyticjournal
        report_invertedanalyticbalance

        ## rules
        analytic_journal_comp_rule
    """)

    for x in xids:
        util.rename_xmlid(cr, 'account.' + x, 'analytic.' + x)
