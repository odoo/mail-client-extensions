from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # view 'account_invoice_report_tree' does not exist in saas3
    util.remove_view(cr, 'sale_crm.account_invoice_report_tree')
