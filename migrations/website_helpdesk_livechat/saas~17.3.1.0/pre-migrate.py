from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_helpdesk_livechat.helpdesk_team_canned_response_menu")
