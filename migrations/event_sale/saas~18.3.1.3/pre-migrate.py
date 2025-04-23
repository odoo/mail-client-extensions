from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_line", "event_slot_id", "int4")
    util.rename_xmlid(
        cr, "event_sale.event_ticket_id_change_exception", "event_sale.event_registration_change_exception"
    )
