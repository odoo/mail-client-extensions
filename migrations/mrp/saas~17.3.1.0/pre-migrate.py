from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.view_mrp_document_form")
    util.remove_view(cr, "mrp.view_document_file_kanban_mrp")
