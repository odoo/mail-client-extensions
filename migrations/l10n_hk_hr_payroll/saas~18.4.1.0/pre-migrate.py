from odoo.upgrade import util


def migrate(cr, version):
    columns = [
        "l10n_hk_mpf_vc_option",
        "l10n_hk_mpf_vc_percentage",
        "l10n_hk_rental_id",
    ]
    move_columns = util.import_script("l10n_au_hr_payroll/saas~18.4.1.0/pre-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    util.remove_view(cr, "l10n_hk_hr_payroll.hr_employee_view_form")
