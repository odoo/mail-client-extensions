from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "project.create.sale.order")
    util.remove_model(cr, "project.create.sale.order.line")
