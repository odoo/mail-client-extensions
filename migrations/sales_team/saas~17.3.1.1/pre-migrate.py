from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sales_team.res_partner_view_team")
    util.remove_field(cr, "res.partner", "team_id")
