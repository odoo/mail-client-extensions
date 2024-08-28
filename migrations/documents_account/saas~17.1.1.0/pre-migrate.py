from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "has_embedded_pdf", "boolean", default=False)
