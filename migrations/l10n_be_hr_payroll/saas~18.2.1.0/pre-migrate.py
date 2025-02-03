from odoo.upgrade import util


def migrate(cr, version):
    xml_ids = [
        "work_entry_type_bank_holiday",
        "work_entry_type_solicitation_time_off",
        "work_entry_type_training",
        "work_entry_type_unjustified_reason",
        "work_entry_type_small_unemployment",
        "work_entry_type_economic_unemployment",
        "work_entry_type_corona",
        "work_entry_type_maternity",
        "work_entry_type_paternity_company",
        "work_entry_type_paternity_legal",
        "work_entry_type_unpredictable",
        "work_entry_type_training",
        "work_entry_type_training_time_off",
        "work_entry_type_flemish_training_time_off",
        "work_entry_type_long_sick",
        "work_entry_type_breast_feeding",
        "work_entry_type_medical_assistance",
        "work_entry_type_youth_time_off",
        "work_entry_type_recovery_additional",
        "work_entry_type_additional_paid",
        "work_entry_type_notice",
        "work_entry_type_phc",
        "work_entry_type_extra_legal",
        "work_entry_type_part_sick",
        "work_entry_type_recovery",
        "work_entry_type_european",
        "work_entry_type_credit_time",
        "work_entry_type_parental_time_off",
        "work_entry_type_simple_holiday_pay_variable_salary",
        "work_entry_type_work_accident",
        "work_entry_type_partial_incapacity",
        "work_entry_type_strike",
    ]
    for xml_id in xml_ids:
        util.force_noupdate(cr, f"l10n_be_hr_payroll.{xml_id}")
