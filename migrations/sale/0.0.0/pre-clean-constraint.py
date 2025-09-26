from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~17.1"):
        util.remove_constraint(cr, "sale_order", "sale_order_name_uniq", warn=False)
