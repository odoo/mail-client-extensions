from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.invite", "has_identical_config")
    util.remove_menus(cr, [util.ref(cr, "appointment.menu_schedule_report_all_events")])
