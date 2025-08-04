from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr,
        "hr_work_entry.l10n_be_work_entry_type_credit_time",
        fields=["l10n_be_is_time_credit"],
        from_module="l10n_be_hr_payroll",
    )
    util.update_record_from_xml(
        cr,
        "hr_work_entry.l10n_be_work_entry_type_parental_time_off",
        fields=["l10n_be_is_time_credit"],
        from_module="l10n_be_hr_payroll",
    )
    util.update_record_from_xml(
        cr,
        "hr_work_entry.l10n_be_work_entry_type_simple_holiday_pay_variable_salary",
        fields=["l10n_be_is_time_credit"],
        from_module="l10n_be_hr_payroll",
    )
