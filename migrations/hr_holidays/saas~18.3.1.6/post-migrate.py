from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_annual_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_sick_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_unpaid_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_marriage_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_maternity_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_paternity_leave", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_holidays.l10n_id_leave_type_bereavement_leave", util.update_record_from_xml)

    util.if_unchanged(cr, "hr_holidays.l10n_sk_leave_type_maternity", util.update_record_from_xml)

    util.if_unchanged(cr, "hr_holidays.l10n_lu_leave_type_situational_unemployment", util.update_record_from_xml)

    util.if_unchanged(
        cr, "hr_holidays.leave_type_sick_time_off", util.update_record_from_xml, fields=["hide_on_dashboard"]
    )
    util.if_unchanged(cr, "hr_holidays.leave_type_unpaid", util.update_record_from_xml, fields=["hide_on_dashboard"])
    util.if_unchanged(cr, "hr_holidays.holiday_status_eto", util.update_record_from_xml, fields=["hide_on_dashboard"])
    util.if_unchanged(
        cr, "hr_holidays.holiday_status_extra_hours", util.update_record_from_xml, fields=["hide_on_dashboard"]
    )
