from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_hk.view_partner_bank_form_inherit_account")
