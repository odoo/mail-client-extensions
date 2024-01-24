# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_attendance.hr_attendance_report_rule_multi_company")
