from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "documents_fsm"):
        util.move_field_to_module(cr, "documents.document", "document_count", "documents", "documents_fsm")
    else:
        util.remove_field(cr, "documents.document", "document_count")
