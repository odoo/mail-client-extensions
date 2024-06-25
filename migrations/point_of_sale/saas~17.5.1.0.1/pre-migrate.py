from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_field(cr, "pos.config", "module_pos_mercury")
    util.remove_field(cr, "res.config.settings", "module_pos_mercury")

    util.rename_field(cr, "pos.order.line", *eb("combo_{line,item}_id"))

    util.rename_xmlid(cr, *eb("point_of_sale.product_jeans_combo_{line,item}_1"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_jeans_combo_{line,item}_2"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_1"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_2"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_3"))
    util.rename_xmlid(cr, *eb("point_of_sale.menu_{pos,product}_combo"))

    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo,product_combo_pos}_manager"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo,product_combo_pos}_user"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo_line,product_combo_item_pos}_manager"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo_line,product_combo_item_pos}_user"))
