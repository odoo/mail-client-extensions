from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_timesheet_enterprise.timesheet_tip_3", util.update_record_from_xml)
