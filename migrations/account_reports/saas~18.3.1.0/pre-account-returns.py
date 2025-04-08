from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.account_report_tree_configure_start_dates")

    util.remove_field(cr, "account.report.annotation", "fiscal_position_id")

    util.remove_field(cr, "account.move", "tax_closing_alert")
    util.remove_field(cr, "res.config.settings", "account_reports_show_per_company_setting")
    util.remove_field(cr, "account.report", "tax_closing_start_date")

    util.rename_field(cr, "res.company", "account_tax_periodicity_reminder_day", "account_return_reminder_day")
    util.rename_field(cr, "res.company", "account_tax_periodicity_journal_id", "account_tax_return_journal_id")
    util.rename_field(cr, "res.company", "account_tax_periodicity", "account_return_periodicity")

    util.rename_field(cr, "res.config.settings", "account_tax_periodicity_reminder_day", "account_return_reminder_day")
    util.rename_field(cr, "res.config.settings", "account_tax_periodicity_journal_id", "account_tax_return_journal_id")
    util.rename_field(cr, "res.config.settings", "account_tax_periodicity", "account_return_periodicity")

    util.rename_field(
        cr, "account.financial.year.op", "account_tax_periodicity_reminder_day", "account_return_reminder_day"
    )
    util.rename_field(
        cr, "account.financial.year.op", "account_tax_periodicity_journal_id", "account_tax_return_journal_id"
    )
    util.rename_field(cr, "account.financial.year.op", "account_tax_periodicity", "account_return_periodicity")

    util.remove_field(cr, "mail.activity", "account_tax_closing_params")
