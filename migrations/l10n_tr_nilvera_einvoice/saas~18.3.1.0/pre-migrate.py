from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_tr_nilvera_einvoice.account_journal_dashboard_kanban_view")
