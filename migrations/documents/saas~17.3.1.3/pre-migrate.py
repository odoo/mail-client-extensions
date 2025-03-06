from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents.module_category_documents_management")
    util.create_column(cr, "documents_facet", "color", "int4")
    # random color from [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    cr.execute("UPDATE documents_facet SET color = (id % 11 + 1)")
