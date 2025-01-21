from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock.report_product_template_replenishment")
    util.remove_view(cr, "stock.report_product_product_replenishment")
    util.remove_view(cr, "stock.report_replenishment_header")
    util.remove_record(cr, "stock.all_picking")
    util.remove_view(cr, "stock.report_stock_inventory")
    util.remove_view(cr, "stock.report_mrp_line")
    util.remove_record(cr, "stock.stock_replenishment_report_product_product_action")
    util.remove_record(cr, "stock.stock_replenishment_report_product_template_action")
    util.remove_record(cr, "stock.stock_replenishment_product_product_action")
    util.rename_model(
        cr,
        "report.stock.report_product_product_replenishment",
        "stock.forecasted_product_product",
        False,  # noqa: FBT003
    )
    util.rename_model(
        cr,
        "report.stock.report_product_template_replenishment",
        "stock.forecasted_product_template",
        False,  # noqa: FBT003
    )

    # `product_id` is required on packagings, deletes the ones without this
    # field as they shouldn't exist at the first place.
    util.explode_execute(cr, "DELETE FROM product_packaging WHERE product_id IS NULL", table="product_packaging")
