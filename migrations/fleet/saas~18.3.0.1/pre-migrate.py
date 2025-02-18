from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "fleet.fleet_vehicle_odometer_view_kanban")
    util.remove_field(cr, "res.partner", "plan_to_change_car")
    util.remove_field(cr, "res.partner", "plan_to_change_bike")
