from odoo.upgrade import util


def migrate(cr, version):
    columns = [
        "l10n_lu_tax_id_number",
        "l10n_lu_tax_classification",
        "l10n_lu_tax_rate_no_classification",
        "l10n_lu_deduction_fd_daily",
        "l10n_lu_deduction_ac_ae_daily",
        "l10n_lu_deduction_ce_daily",
        "l10n_lu_deduction_ds_daily",
        "l10n_lu_deduction_fo_daily",
        "l10n_lu_deduction_amd_daily",
        "l10n_lu_package_ffo_daily",
        "l10n_lu_package_fds_daily",
        "l10n_lu_tax_credit_cis",
        "l10n_lu_tax_credit_cip",
        "l10n_lu_tax_credit_cim",
    ]

    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.hr_contract{,_template}_view_form"))
