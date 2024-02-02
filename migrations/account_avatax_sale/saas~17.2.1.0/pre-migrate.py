from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "account_avatax_sale.report_invoice_document", "account_avatax_sale.report_saleorder_document"
    )
