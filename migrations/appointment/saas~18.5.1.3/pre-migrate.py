from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.invite", "has_identical_config")
