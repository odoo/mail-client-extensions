from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "l10n_hk_mpf_vc_option")
    util.make_field_non_stored(cr, "hr.employee", "l10n_hk_mpf_vc_percentage")
    util.make_field_non_stored(cr, "hr.employee", "l10n_hk_rental_id")
