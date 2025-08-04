from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr,
        "hr_work_entry.l10n_hk_work_entry_type_paternity_leave_80",
        fields=["l10n_hk_use_713"],
        from_module="l10n_hk_hr_payroll",
    )
    util.update_record_from_xml(
        cr,
        "hr_holidays.l10n_hk_leave_type_paternity_leave_80",
        fields=["work_entry_type_id"],
        from_module="hr_work_entry_holidays",
    )
