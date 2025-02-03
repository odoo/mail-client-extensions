from odoo.upgrade import util


def migrate(cr, version):
    xml_ids = [
        "work_entry_type_sick_leave_80",
        "work_entry_type_compassionate_leave",
        "work_entry_type_marriage_leave",
        "work_entry_type_examination_leave",
        "work_entry_type_maternity_leave",
        "work_entry_type_maternity_leave_80",
        "work_entry_type_paternity_leave",
        "work_entry_type_statutory_holiday",
        "work_entry_type_public_holiday",
        "work_entry_type_weekend",
    ]
    for xml_id in xml_ids:
        util.force_noupdate(cr, f"l10n_hk_hr_payroll.{xml_id}")
