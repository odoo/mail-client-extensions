from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "mrp_workorder.additional.product")
