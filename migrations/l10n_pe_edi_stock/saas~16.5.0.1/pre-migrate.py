from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_pe_edi_stock.view_prod_form_inh_l10n_mx")
