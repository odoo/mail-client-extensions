from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
      UPDATE res_lang
         SET code = 'sr@Cyrl',
             iso_code = 'sr@Cyrl'
       WHERE code = 'sr_RS'
        """
    )
    util.rename_xmlid(cr, "base.lang_sr_RS", "base.lang_sr@Cyrl")
    util.remove_view(cr, "base.res_users_identitycheck_view_form_revokedevices")

    util.move_field_to_module(cr, "res.bank", "country_code", "l10n_pe", "base")
    util.move_field_to_module(cr, "res.bank", "country_code", "l10n_hk_hr_payroll", "base")
