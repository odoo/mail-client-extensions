from odoo.upgrade import util


def migrate(cr, version):
    # Update amount_rate field for US-specific work entry types
    us_work_entry_types = [
        ("hr_work_entry.l10n_us_work_entry_type_double"),
        ("hr_work_entry.l10n_us_work_entry_type_retro_overtime"),
    ]
    for xmlid in us_work_entry_types:
        util.update_record_from_xml(cr, xmlid, fields=["amount_rate"])

    # Update amount_rate field for SK-specific work entry types
    sk_work_entry_types = [
        ("hr_work_entry.l10n_sk_work_entry_type_sick_25"),
        ("hr_work_entry.l10n_sk_work_entry_type_sick_55"),
        ("hr_work_entry.l10n_sk_work_entry_type_sick_0"),
        ("hr_work_entry.l10n_sk_work_entry_type_maternity"),
        ("hr_work_entry.l10n_sk_work_entry_type_parental_time_off"),
    ]
    for xmlid in sk_work_entry_types:
        util.update_record_from_xml(cr, xmlid, fields=["amount_rate"])

    util.remove_field(cr, "hr.work.entry.regeneration.wizard", "validated_work_entry_ids")
