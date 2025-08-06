from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move", "move_orig_fifo_ids")
    # Prevent the computation of 'l10n_mx_edi_can_use_customs_invoicing'
    util.create_column(cr, "sale_order_line", "l10n_mx_edi_can_use_customs_invoicing", "boolean")
