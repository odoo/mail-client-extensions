from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_calendar.view_calendar_event_form")
    util.remove_view(cr, "hr_calendar.view_calendar_event_form_quick_create")
