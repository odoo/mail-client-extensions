from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_documents.document_view_form")
