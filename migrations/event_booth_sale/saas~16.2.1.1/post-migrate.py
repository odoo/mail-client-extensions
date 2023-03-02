from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "event.booth.category", ["price_incl"])
