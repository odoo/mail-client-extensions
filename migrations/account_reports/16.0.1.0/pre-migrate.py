from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.account_reports_journal_dashboard_kanban_view_account_manager")
