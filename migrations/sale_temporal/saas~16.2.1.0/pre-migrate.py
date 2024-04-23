from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.temporal.recurrence", "subscription_unit_display", "temporal_unit_display")
    util.convert_field_to_html(cr, "sale.order", "internal_note")
    util.convert_field_to_translatable(cr, "sale.temporal.recurrence", "name")
