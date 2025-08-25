from odoo.tools import sql

from odoo.upgrade import util


def migrate(cr, version):
    sql.rename_column(cr, "l10n_au_super_fund", "display_name", "name")
    util.make_field_non_stored(cr, "l10n_au.super.fund", "display_name", selectable=True)
    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_ato_rate_limit")

    util.change_field_selection_values(cr, "hr.payslip.input.type", "l10n_au_paygw_treatment", {"special": "excess"})
    util.change_field_selection_values(cr, "hr.payslip.input.type", "l10n_au_payment_type", {"other": "lump_sum"})

    util.rename_xmlid(
        cr,
        "l10n_au_hr_payroll.input_bonus_commissions_overtime_prior",
        "l10n_au_hr_payroll.input_bonus_commissions_overtime",
    )
    # Input types merged
    input_types_to_switch = {
        util.ref(cr, "l10n_au_hr_payroll.input_bonus_commissions_prior"): util.ref(
            cr, "l10n_au_hr_payroll.input_bonus_commissions"
        ),
        util.ref(cr, "l10n_au_hr_payroll.input_cents_per_kilometer_1"): util.ref(
            cr, "l10n_au_hr_payroll.input_cents_per_kilometer_2"
        ),
        util.ref(cr, "l10n_au_hr_payroll.input_laundry_1"): util.ref(cr, "l10n_au_hr_payroll.input_laundry_2"),
        util.ref(cr, "l10n_au_hr_payroll.input_overseas_travel_allowance_1"): util.ref(
            cr, "l10n_au_hr_payroll.input_overseas_travel_allowance_2"
        ),
        util.ref(cr, "l10n_au_hr_payroll.input_overtime_meal_allowance_1"): util.ref(
            cr, "l10n_au_hr_payroll.input_overtime_meal_allowance_2"
        ),
        util.ref(cr, "l10n_au_hr_payroll.input_domestic_travel_allowance_3"): util.ref(
            cr, "l10n_au_hr_payroll.input_domestic_travel_allowance_1"
        ),
    }
    util.replace_record_references_batch(cr, input_types_to_switch, "hr.payslip.input.type")

    # Input types not be used
    util.delete_unused(cr, "l10n_au_hr_payroll.l10n_au_lumpsum_e", deactivate=True)
    util.delete_unused(cr, "l10n_au_hr_payroll.input_living_away_from_home_allowance", deactivate=True)
    util.delete_unused(cr, "l10n_au_hr_payroll.input_voluntary_super_contribution", deactivate=True)
    util.delete_unused(cr, "l10n_au_hr_payroll.input_salary_sacrifice_superannuation", deactivate=True)
    util.delete_unused(cr, "l10n_au_hr_payroll.input_salary_sacrifice_other", deactivate=True)
