from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "choose.delivery.package", "manual_measurement")
