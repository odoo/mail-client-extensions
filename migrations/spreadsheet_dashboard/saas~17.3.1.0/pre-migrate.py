from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "spreadsheet_dashboard.group_dashboard_manager", noupdate=False)
    util.remove_record(cr, "spreadsheet_dashboard.dashboard_management")
