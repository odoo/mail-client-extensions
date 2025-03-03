from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "spreadsheet_revision", "author_id", "integer")
    query = """
        UPDATE spreadsheet_revision r
           SET author_id = r.create_uid
    """
    util.explode_execute(cr, query, table="spreadsheet_revision", alias="r")
