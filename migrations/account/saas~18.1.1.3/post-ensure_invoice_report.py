from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM ir_model_data
         WHERE module = 'account'
           AND name = 'account_invoices'
           AND noupdate
        """
    )
    if cr.rowcount:
        util.update_record_from_xml(cr, "account.account_invoices", fields=["is_invoice_report"])
