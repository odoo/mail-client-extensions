from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "bus_presence", "bus_presence_bus_user_presence_unique")
