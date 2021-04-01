from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account.view_account_invoice_report_tree")
