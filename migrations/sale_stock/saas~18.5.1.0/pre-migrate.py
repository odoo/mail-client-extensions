from odoo.upgrade import util


def migrate(cr, version):
    util.convert_m2o_field_to_m2m(
        cr,
        "stock.reference",
        "sale_id",
        new_name="sale_ids",
        m2m_table="stock_reference_sale_rel",
        col1="reference_id",
        col2="sale_id",
    )
    util.convert_m2o_field_to_m2m(
        cr,
        "sale.order",
        "procurement_group_id",
        new_name="stock_reference_ids",
        m2m_table="stock_reference_sale_rel",
        col1="sale_id",
        col2="reference_id",
    )
