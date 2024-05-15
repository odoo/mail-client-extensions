from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE res_country SET currency_id=%s WHERE code='ZW'",
        [util.ref(cr, "base.ZIG")],
    )
    util.delete_unused(cr, "base.ZWL")
