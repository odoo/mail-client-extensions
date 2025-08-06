from odoo.upgrade import util


def migrate(cr, version):
    # Computed field on fleet.vehicle.model
    if util.module_installed(cr, "l10n_be_hr_payroll_fleet"):
        cr.execute("""SELECT id FROM fleet_vehicle_model WHERE _upg_is_default_mx_model IS TRUE""")
        fleet_vehicle_model_ids = [row[0] for row in cr.fetchall()]
        if fleet_vehicle_model_ids:
            util.recompute_fields(cr, "fleet.vehicle.model", ["default_co2"], ids=fleet_vehicle_model_ids)
    util.remove_column(cr, "fleet_vehicle_model", "_upg_is_default_mx_model")

    # Computed field on fleet.vehicle
    cr.execute("""SELECT id FROM fleet_vehicle WHERE _upg_orig_l10n_mx_vehicle_id IS NOT NULL""")
    fleet_vehicle_ids = [row[0] for row in cr.fetchall()]
    if util.module_installed(cr, "hr_fleet") and fleet_vehicle_ids:
        util.recompute_fields(cr, "fleet.vehicle", ["driver_employee_id"], ids=fleet_vehicle_ids)
    util.remove_column(cr, "fleet_vehicle", "_upg_orig_l10n_mx_vehicle_id")
