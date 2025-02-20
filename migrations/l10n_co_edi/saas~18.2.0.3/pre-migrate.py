from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_co_edi.address")
    util.remove_view(cr, "l10n_co_edi.partner_info")
