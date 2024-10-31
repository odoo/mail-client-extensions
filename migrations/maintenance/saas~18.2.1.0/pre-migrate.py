from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "maintenance.equipment", "location", drop_column=False)
