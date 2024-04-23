from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "spreadsheet_revision", "res_model", "varchar")
    util.create_column(cr, "spreadsheet_revision", "res_id", "int4")
    query = """
        UPDATE spreadsheet_revision r
           SET res_model = 'documents.document',
               res_id = r.document_id
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="spreadsheet_revision", alias="r"))
    util.remove_constraint(cr, "spreadsheet_revision", "spreadsheet_revision_parent_revision_unique")
    util.remove_field(cr, "spreadsheet.revision", "document_id")
