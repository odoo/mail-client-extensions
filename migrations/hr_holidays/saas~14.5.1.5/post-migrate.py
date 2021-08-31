# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays.holiday_status_cl", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_sl", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_comp", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_unpaid", util.update_record_from_xml)
