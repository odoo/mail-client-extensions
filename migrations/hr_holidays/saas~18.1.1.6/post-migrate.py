from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays.holiday_status_cl", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_sl", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_comp", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.holiday_status_unpaid", util.update_record_from_xml)

    # Update access rules to include country restriction on time off types
    util.if_unchanged(cr, "hr_holidays.hr_holidays_status_rule_multi_company", util.update_record_from_xml)
