from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "event.event.ticket", ["price_incl"])
