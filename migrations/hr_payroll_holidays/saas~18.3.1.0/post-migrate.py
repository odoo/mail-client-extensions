from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_payroll_holidays.ir_actions_server_mark_as_reported", util.update_record_from_xml)
