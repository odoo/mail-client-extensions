from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT 1 FROM res_partner WHERE l10n_in_shipping_gstin IS NOT NULL LIMIT 1")
    drop_column = not bool(cr.rowcount)
    util.remove_field(cr, "res.partner", "l10n_in_shipping_gstin", drop_column=drop_column)
    util.remove_view(cr, "l10n_in_sale.l10n_in_view_partner_form")
