# -*- coding: utf-8 -*-
def migrate(cr, version):
    # in 8.0, size has been removed from a lot of varchar fields
    # to be successful, we need to drop views that depends on these fields
    # NOTE not all views are listed here, only the ones that forbid migration
    # NOTE some views are relics from 6.1
    # please order them alphabetically, to ease seach
    views = """
        account_entries_report
        asset_asset_report
        analytic_entries_report
        hr_holidays_remaining_leaves_user
        project_vs_remaining_hours
        report_aged_receivable
        report_document_user
        report_files_partner
        report_invoice_created
        timesheet_report
    """.split()

    for v in views:
        cr.execute('DROP VIEW IF EXISTS "%s"' % (v,))
