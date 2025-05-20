from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_id_number")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_classification")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_rate_no_classification")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_fd_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_ac_ae_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_ce_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_ds_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_fo_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_deduction_amd_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_package_ffo_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_package_fds_daily")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_credit_cis")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_credit_cip")
    util.make_field_non_stored(cr, "hr.employee", "l10n_lu_tax_credit_cim")
