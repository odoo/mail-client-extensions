from odoo.upgrade import util


def migrate(cr, version):
    # Move the "aba_bsb" field from l10n_au_aba to l10n_au, if it exists.
    util.move_field_to_module(cr, "res.partner.bank", "aba_bsb", "l10n_au_aba", "l10n_au")

    # Move the "view_partner_bank_form_id" from l10n_au_aba to l10n_au, if it exists.
    util.rename_xmlid(cr, "l10n_au_aba.view_partner_bank_form", "l10n_au.view_partner_bank_form")
