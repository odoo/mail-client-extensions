from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~17.5"):
        util.remove_field(cr, "sale.order", "project_id")
