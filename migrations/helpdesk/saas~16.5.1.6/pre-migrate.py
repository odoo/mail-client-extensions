from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "display_alias_name")
