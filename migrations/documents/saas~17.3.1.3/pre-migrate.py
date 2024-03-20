from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents.module_category_documents_management")
