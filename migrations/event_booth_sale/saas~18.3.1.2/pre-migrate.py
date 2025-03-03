from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "is_event_booth")
