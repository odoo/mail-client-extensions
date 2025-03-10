from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_template", "publish_date", "timestamp without time zone")
    query = "UPDATE product_template SET publish_date = create_date"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="product_template"))
    util.change_field_selection_values(
        cr,
        "website",
        "shop_default_sort",
        {"create_date desc": "publish_date desc"},
    )
