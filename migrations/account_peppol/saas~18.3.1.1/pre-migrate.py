from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_peppol.account_journal_dashboard_kanban_view")
