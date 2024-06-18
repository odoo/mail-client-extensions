from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "pos.config", ["certifiedBlackboxIdentifier"], chunk_size=1)
