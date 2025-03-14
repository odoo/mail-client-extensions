from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "delivery.carrier", ["country_id"])
