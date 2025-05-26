from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave", "manager_id")
