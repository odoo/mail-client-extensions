from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "portal_show_rating")
    util.remove_view(cr, "helpdesk.team_rating_page")
    util.remove_constraint(cr, "helpdesk_team", "helpdesk_team_not_portal_show_rating_if_not_use_rating")
