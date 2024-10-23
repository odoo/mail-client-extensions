from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "res_company", "l10n_br_ie_code")
    util.remove_column(cr, "res_company", "l10n_br_im_code")
    util.remove_field(cr, "res.company", "l10n_br_cpf_code")
