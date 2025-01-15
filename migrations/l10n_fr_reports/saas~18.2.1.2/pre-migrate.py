from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_fr_reports.inherit_view_account_journal_dashboard_kanban")
