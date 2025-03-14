from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_helpdesk_livechat.im_livechat_canned_response_view_tree_inherit_helpdesk")
    util.remove_view(cr, "website_helpdesk_livechat.im_livechat_canned_response_view_search")

    util.remove_record(cr, "website_helpdesk_livechat.helpdesk_im_livechat_canned_response_action")
