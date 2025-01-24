from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "documents.document", "name")
    util.create_column(cr, "documents_document", "sequence", "int4", default=10)
