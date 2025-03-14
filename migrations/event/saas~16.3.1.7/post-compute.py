from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "event.registration", ["company_name"])
