from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "event_sale.event_registration_view_kanban")
    util.rename_field(cr, "event.event", "sale_price_subtotal", "sale_price_total")
