from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract.salary.offer", "show_new_car")
