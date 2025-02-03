from odoo.upgrade import util


def migrate(cr, version):
    xml_ids = [
        "l10n_au_work_entry_paid_time_off",
        "l10n_au_work_entry_long_service_leave",
        "l10n_au_work_entry_personal_leave",
        "l10n_au_work_entry_type_other",
        "l10n_au_work_entry_type_parental",
        "l10n_au_work_entry_type_compensation",
        "l10n_au_work_entry_type_defence",
        "l10n_au_work_entry_type_cash_out",
        "l10n_au_work_entry_type_termination",
        "l10n_au_work_entry_type_overtime_regular",
        "l10n_au_work_entry_type_overtime_saturday",
        "l10n_au_work_entry_type_overtime_sunday",
        "l10n_au_work_entry_type_overtime_pto",
        "l10n_au_work_entry_type_overtime_saturday_pto",
        "l10n_au_work_entry_type_overtime_sunday_pto",
    ]
    for xml_id in xml_ids:
        util.force_noupdate(cr, f"l10n_au_hr_payroll.{xml_id}")
