from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "l10n.be.double.pay.recovery.wizard", "contract_id", "version_id")
    util.rename_field(cr, "l10n_be.hr.payroll.schedule.change.wizard", "contract_id", "version_id")
    util.rename_field(cr, "l10n_be.schedule.change.allocation", "contract_id", "version_id")
    util.rename_field(cr, "l10n.be.december.slip.wizard", "contract_id", "version_id")

    columns = [
        "spouse_fiscal_status",
        "disabled_spouse_bool",
        "disabled_children_bool",
        "disabled_children_number",
        "l10n_be_dependent_children_attachment",
        "other_dependent_people",
        "other_senior_dependent",
        "other_disabled_senior_dependent",
        "other_juniors_dependent",
        "other_disabled_juniors_dependent",
    ]
    # Field doesn't exist in 18.0 and thus is treated separately
    if util.column_exists(cr, "hr_employee", "fiscal_voluntarism"):
        columns.append("fiscal_voluntarism")

    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    util.remove_view(cr, "l10n_be_hr_payroll.res_users_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_employee_form__l10n_be_view_for")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_contract_view_form")

    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.hr_payroll_dashboard_warning_invalid_{gender,sex}"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.hr_employee_{form_l10n_payroll,view_form}"))
