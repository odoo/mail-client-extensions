from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "im_livechat.im_livechat_canned_response_view_tree")
    util.remove_record(cr, "im_livechat.im_livechat_canned_response_action")
