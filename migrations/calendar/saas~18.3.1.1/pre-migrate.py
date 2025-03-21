from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_calendar"):
        util.move_field_to_module(cr, "calendar.event", "unavailable_partner_ids", "hr_calendar", "calendar")
    util.rename_field(cr, "calendar.popover.delete.wizard", "record", "calendar_event_id")
