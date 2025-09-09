from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = "SELECT id FROM pos_order WHERE currency_rate IS NULL"
    util.recompute_fields(cr, "pos.order", fields=["currency_rate"], query=query)
