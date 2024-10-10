from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_fr_account.res_partner_form_l10n_fr")
