from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "feature_form_url")
    util.remove_view(cr, "website_helpdesk_form.helpdesk_team_view_form_inherit_website_helpdesk_form")
