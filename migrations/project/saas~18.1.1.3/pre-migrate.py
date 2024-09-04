from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_milestone", "sequence", "integer", default=10)
