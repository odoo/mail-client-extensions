from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays.hr_leave_rule_multicompany", util.update_record_from_xml)
