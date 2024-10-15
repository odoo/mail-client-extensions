from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "appointment_type", "slot_creation_interval", "numeric")
    cr.execute(
        "UPDATE appointment_type SET slot_creation_interval = appointment_duration WHERE appointment_duration > 0"
    )
