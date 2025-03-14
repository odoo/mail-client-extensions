from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "event.event_type_data_ticket")
    util.delete_unused(cr, "event.event_type_data_conference")
