from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    break_recursive_loops(cr, "uom.uom", "relative_uom_id")
    env = util.env(cr)
    uom_hour = env.ref("uom.product_uom_hour", raise_if_not_found=False)
    uom_day = env.ref("uom.product_uom_day", raise_if_not_found=False)
    day_hour_factor = 8.0
    # add context to skip the constraint in stock module
    if uom_hour:
        if uom_day and uom_day == uom_hour.relative_uom_id:
            day_hour_factor = round(1 / uom_hour.relative_factor, 5)
        if uom_hour.relative_factor != 1.0 or uom_hour.relative_uom_id:
            uom_hour.with_context(_upg_swap_time_uom_ref=True).write({"relative_uom_id": False, "relative_factor": 1.0})
        if uom_day and not uom_day.relative_uom_id:
            uom_day.with_context(_upg_swap_time_uom_ref=True).write(
                {"relative_uom_id": uom_hour, "relative_factor": day_hour_factor}
            )
