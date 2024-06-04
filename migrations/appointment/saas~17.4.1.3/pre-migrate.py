from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "appointment.appointment_default_resource_calendar", util.update_record_from_xml)
