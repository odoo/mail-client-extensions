from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_management.report_saleorder_document_inherit_sale_management")
