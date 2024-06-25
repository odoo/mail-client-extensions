from odoo.tools import sql

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.module_installed(cr, "point_of_sale"):
        util.move_model(
            cr, "pos.combo", "point_of_sale", "product", keep=("access_pos_combo_manager", "access_pos_combo_user")
        )
        util.move_model(
            cr,
            "pos.combo.line",
            "point_of_sale",
            "product",
            keep=("access_pos_combo_line_manager", "access_pos_combo_line_user"),
        )

        util.rename_model(cr, *eb("{pos,product}.combo"))
        util.rename_model(cr, "pos.combo.line", "product.combo.item")
        util.rename_table(cr, *eb("{pos,product}_combo_product_template_rel"))
        sql.rename_column(cr, "product_combo_product_template_rel", *eb("{pos,product}_combo_id"))

        util.rename_field(cr, "product.combo", *eb("combo_{line,item}_ids"))
        util.rename_field(cr, "product.combo", "num_of_products", "combo_item_count")
        util.rename_field(cr, "product.combo.item", "combo_price", "extra_price")

        util.move_field_to_module(cr, "product.template", "combo_ids", "point_of_sale", "product")

        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_organizer"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_organizer_product_template"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_pad"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.monitor_stand"))

        util.rename_xmlid(cr, *eb("{point_of_sale,product}.size_attribute"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.size_attribute_s"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.size_attribute_m"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.size_attribute_l"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_organizer_size"))

        util.rename_xmlid(cr, *eb("{point_of_sale,product}.fabric_attribute"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.fabric_attribute_plastic"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.fabric_attribute_leather"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.fabric_attribute_custom"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_organizer_fabric"))

        util.rename_xmlid(cr, "point_of_sale.desk_organizer_combo_line", "product.desk_organizer_combo_item")
        util.rename_xmlid(cr, "point_of_sale.desk_pad_combo_line", "product.desk_pad_combo_item")
        util.rename_xmlid(cr, "point_of_sale.monitor_stand_combo_line", "product.monitor_stand_combo_item")
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desk_accessories_combo"))
        util.rename_xmlid(cr, "point_of_sale.product_3_combo_line", "product.product_3_combo_item")
        util.rename_xmlid(cr, "point_of_sale.product_5_combo_line", "product.product_5_combo_item")
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.desks_combo"))
        util.rename_xmlid(cr, "point_of_sale.product_11_combo_line", "product.product_11_combo_item")
        util.rename_xmlid(cr, "point_of_sale.product_11b_combo_line", "product.product_11b_combo_item")
        util.rename_xmlid(cr, "point_of_sale.product_12_combo_line", "product.product_12_combo_item")
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.chairs_combo"))
        util.rename_xmlid(cr, *eb("{point_of_sale,product}.office_combo"))

        util.rename_xmlid(cr, "product.view_pos_combo_form", "product.product_combo_view_form")
        util.rename_xmlid(cr, "product.view_pos_combo_tree", "product.product_combo_view_tree")
        util.rename_xmlid(cr, "product.action_pos_combo", "product.product_combo_action")
