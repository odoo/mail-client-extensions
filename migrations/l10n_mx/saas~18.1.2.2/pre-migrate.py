from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx.view_res_partner_inherit_l10n_mx_edi_bank")
