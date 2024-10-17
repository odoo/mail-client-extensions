from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "stock.picking", *eb("l10n_in_ewaybill_id{,s}"))
    util.rename_field(cr, "stock.move", *eb("l10n_in_ewaybill_id{,s}"))
    util.remove_field(cr, "l10n.in.ewaybill", "picking_type_code")
    util.remove_view(cr, "l10n_in_ewaybill_stock.l10n_in_ewaybill_form_view")
