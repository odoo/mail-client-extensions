from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "pos.config", *eb("module_pos{_restaurant,}_appointment"))
    util.rename_field(cr, "res.config.settings", *eb("pos_module_pos{_restaurant,}_appointment"))
    util.remove_view(cr, "point_of_sale.view_partner_pos_kanban")
