from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.rename_model(cr, "pos_preparation_display.display", "pos.prep.display")
    util.rename_model(cr, "pos_preparation_display.stage", "pos.prep.stage")
    util.rename_model(cr, "pos_preparation_display.order", "pos.prep.order")
    util.rename_model(cr, "pos_preparation_display.orderline", "pos.prep.line")
    util.rename_model(cr, "pos_preparation_display.reset.wizard", "pos.preparation.display.reset.wizard")

    util.remove_field(cr, "pos.prep.order", "displayed")
    util.remove_field(cr, "pos.prep.order", "pos_config_id")
    util.remove_field(cr, "pos.prep.order", "order_stage_ids")
    util.rename_field(cr, "pos.prep.order", "preparation_display_order_line_ids", "prep_line_ids")

    util.rename_field(cr, "pos.prep.order", "pdis_general_note", "pdis_general_customer_note")

    util.rename_field(cr, "pos.prep.line", "product_quantity", "quantity")
    util.rename_field(cr, "pos.prep.line", "product_cancelled", "cancelled")
    util.rename_field(cr, "pos.prep.line", "preparation_display_order_id", "prep_order_id")

    util.rename_field(cr, "pos.prep.stage", "preparation_display_id", "prep_display_id")

    util.rename_xmlid(cr, *eb("pos_enterprise.{index,prep_display_index}"))
