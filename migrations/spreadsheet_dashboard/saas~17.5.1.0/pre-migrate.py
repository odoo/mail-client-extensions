from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "spreadsheet_dashboard_event_sale.spreadsheet_dashboard_group_marketing",
        "spreadsheet_dashboard.spreadsheet_dashboard_group_marketing",
    )
