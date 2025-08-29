from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~18.3"):
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_annual_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_sick_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_unpaid_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_marriage_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_maternity_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_paternity_leave", util.update_record_from_xml)
        util.if_unchanged(cr, "l10n_id_hr_payroll.holiday_type_id_bereavement_leave", util.update_record_from_xml)
