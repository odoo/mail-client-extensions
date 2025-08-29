from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.pos_iot_config_view_form")
    util.make_field_non_stored(cr, "res.config.settings", "pos_epson_printer_ip", selectable=True)

    util.convert_m2o_field_to_m2m(
        cr,
        "pos.order",
        "procurement_group_id",
        new_name="stock_reference_ids",
        m2m_table="stock_reference_pos_order_rel",
        col1="reference_id",
        col2="pos_order_id",
    )
    util.convert_m2o_field_to_m2m(
        cr,
        "stock.reference",
        "pos_order_id",
        new_name="pos_order_ids",
        m2m_table="stock_reference_pos_order_rel",
        col1="pos_order_id",
        col2="reference_id",
    )
