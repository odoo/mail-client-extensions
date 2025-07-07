from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "spreadsheet_revision", "revision_date", "timestamp without time zone")
    query = """
        UPDATE spreadsheet_revision r
           SET revision_date = r.create_date
    """
    util.explode_execute(cr, query, table="spreadsheet_revision", alias="r")
