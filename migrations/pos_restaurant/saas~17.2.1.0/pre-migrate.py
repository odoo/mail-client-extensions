from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "pos.config",
        "self_ordering_alternative_fp_id",
        "pos_self_order",
        "pos_restaurant",
    )
    util.rename_field(cr, "pos.config", "self_ordering_alternative_fp_id", "takeaway_fp_id")
    util.move_field_to_module(
        cr,
        "res.config.settings",
        "pos_self_ordering_alternative_fp_id",
        "pos_self_order",
        "pos_restaurant",
    )
    util.rename_field(
        cr,
        "res.config.settings",
        "pos_self_ordering_alternative_fp_id",
        "pos_takeaway_fp_id",
    )
    util.move_field_to_module(
        cr,
        "pos.order",
        "take_away",
        "pos_self_order",
        "pos_restaurant",
    )
    util.rename_field(cr, "pos.order", "take_away", "takeaway")
    util.create_column(cr, "pos_config", "takeaway", "boolean")
    if util.column_exists(cr, "pos_config", "self_ordering_takeaway"):
        cr.execute("UPDATE pos_config SET takeaway = self_ordering_takeaway")
    util.remove_field(cr, "pos.config", "iface_orderline_notes")
    util.remove_field(cr, "res.config.settings", "pos_iface_orderline_notes")
