from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_contract_salary_holidays.holiday_status_eto", util.update_record_from_xml)
