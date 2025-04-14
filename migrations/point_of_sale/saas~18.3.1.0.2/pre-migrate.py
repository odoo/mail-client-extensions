from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "pos.config", *eb("module_pos{_restaurant,}_appointment"))
    util.rename_field(cr, "res.config.settings", *eb("pos_module_pos{_restaurant,}_appointment"))
    util.remove_view(cr, "point_of_sale.view_partner_pos_kanban")

    util.remove_field(cr, "pos.config", "orderlines_sequence_in_cart_by_category")
    util.remove_field(cr, "res.config.settings", "module_pos_preparation_display")
    util.remove_field(cr, "res.config.settings", "pos_orderlines_sequence_in_cart_by_category")

    if util.column_exists(cr, "pos_preset", "name"):
        util.convert_field_to_translatable(cr, "pos.preset", "name")
