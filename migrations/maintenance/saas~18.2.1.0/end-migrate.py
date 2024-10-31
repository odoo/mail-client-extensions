from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "maintenance_equipment", "location")
