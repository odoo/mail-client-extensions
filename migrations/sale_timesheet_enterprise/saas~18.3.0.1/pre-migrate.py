from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_timesheet_enterprise.timesheet_tip_2")
    util.remove_record(cr, "sale_timesheet_enterprise.timesheet_tip_5")
