from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "billable_percentage")
