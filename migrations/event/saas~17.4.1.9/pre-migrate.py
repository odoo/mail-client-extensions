from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "whatsapp_event"):
        util.move_field_to_module(cr, "event.registration", "date_range", "whatsapp_event", "event")
        util.rename_field(cr, "event.registration", "date_range", "event_date_range")
