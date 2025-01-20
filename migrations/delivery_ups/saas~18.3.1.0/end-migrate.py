from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "delivery_carrier", "ups_cod")
