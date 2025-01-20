from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    break_recursive_loops(cr, "uom.uom", "relative_uom_id")
    env = util.env(cr)
    uom_hour = env.ref("uom.product_uom_hour", raise_if_not_found=False)
    if uom_hour:
        if uom_hour.relative_factor != 1.0 or uom_hour.relative_uom_id:
            uom_hour.write({"relative_uom_id": False, "relative_factor": 1.0})
        uom_day = env.ref("uom.product_uom_day", raise_if_not_found=False)
        if uom_day and uom_day.relative_factor != 8.0:
            uom_day.write({"relative_uom_id": uom_hour, "relative_factor": 8.0})
