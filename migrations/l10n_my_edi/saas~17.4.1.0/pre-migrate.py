from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_my_edi.ubl_20_AddressType_my")
    util.remove_view(cr, "l10n_my_edi.ubl_20_PartyType_my")
