from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "timesheet_grid.timesheet_line_rule_user_update-unlink")
