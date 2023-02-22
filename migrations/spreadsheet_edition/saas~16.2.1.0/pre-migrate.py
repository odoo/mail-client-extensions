from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "spreadsheet.collaborative.mixin", "raw", "spreadsheet_data")

    renames = """
        spreadsheet_revision_view_tree
        spreadsheet_revision_view_search
        spreadsheet_revision_action
        menu_technical_spreadsheet
        menu_technical_spreadsheet_revision
    """
    for name in util.splitlines(renames):
        util.rename_xmlid(cr, f"documents_spreadsheet.{name}", f"spreadsheet_edition.{name}")
