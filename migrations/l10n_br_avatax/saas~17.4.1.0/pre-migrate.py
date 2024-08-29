from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_br_avatax.view_product_template_form")
    util.remove_view(cr, "l10n_br_avatax.res_partner_view_form")
