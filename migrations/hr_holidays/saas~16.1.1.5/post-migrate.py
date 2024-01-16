# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays.hr_leave_rule_employee_unlink", util.update_record_from_xml)
