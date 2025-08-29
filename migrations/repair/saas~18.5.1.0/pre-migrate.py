from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "repair.order", "is_returned")
    util.remove_field(cr, "stock.picking", "is_repairable")
    util.remove_field(cr, "stock.picking.type", "is_repairable")
    util.remove_field(cr, "stock.picking.type", "return_type_of_ids")

    util.convert_m2o_field_to_m2m(
        cr,
        "repair.order",
        "procurement_group_id",
        new_name="reference_ids",
        m2m_table="stock_reference_repair_rel",
        col1="repair_id",
        col2="reference_id",
    )
