from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "show_task_button")
