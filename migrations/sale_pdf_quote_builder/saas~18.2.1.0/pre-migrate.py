from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.order", "available_product_document_ids", "available_quotation_document_ids")
