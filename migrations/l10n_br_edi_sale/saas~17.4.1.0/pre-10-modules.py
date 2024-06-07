from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_br_edi_sale.order_form_inherit")
