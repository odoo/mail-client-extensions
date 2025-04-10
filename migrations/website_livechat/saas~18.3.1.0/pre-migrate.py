from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_livechat.im_livechat_channel_rule_public")

    util.remove_view(cr, "website_livechat.im_livechat_channel_form_view")
    util.remove_view(cr, "website_livechat.channel_list_page")
    util.remove_view(cr, "website_livechat.channel_page")

    util.remove_field(cr, "im_livechat.channel", "website_description")
    util.remove_inherit_from_model(cr, "im_livechat.channel", "website.published.mixin")
