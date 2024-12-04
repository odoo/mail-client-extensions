from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.team.member", "mobile")
