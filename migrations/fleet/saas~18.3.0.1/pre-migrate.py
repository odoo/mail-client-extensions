from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "fleet.fleet_vehicle_odometer_view_kanban")
