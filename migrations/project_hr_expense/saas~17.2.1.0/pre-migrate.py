from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "expenses_count")
