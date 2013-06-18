from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """As deleted xmlid are deleted only at the end of the update, deleted
       views still exists in database during the update process and used when
       applying the view inheritance. If the views use a deleted field,
       this raise an error. We delete it ourself to avoid this.
    """
    util.remove_record(cr, 'account_analytic_plans.invoice_supplier_form_inherit')
    util.remove_record(cr, 'account_analytic_plans.view_invoice_line_form_inherit')
