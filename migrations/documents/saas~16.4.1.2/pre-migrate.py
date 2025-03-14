from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "url_preview_image", "varchar")
