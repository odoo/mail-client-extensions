# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.if_unchanged(cr, "im_livechat.mail_shortcode_data_hello", util.update_record_from_xml)

    # Rename mail.channel to discuss.channel
    util.rename_field(cr, "chatbot.message", *eb("{mail,discuss}_channel_id"))
    xmlids = """
        im_livechat.im_livechat_rule_manager_read_all_{mail,discuss}_channel
        im_livechat.{mail,discuss}_channel_action_form
        im_livechat.{mail,discuss}_channel_action_from_livechat_channel
        im_livechat.{mail,discuss}_channel_action_livechat_form
        im_livechat.{mail,discuss}_channel_action_livechat_tree
        im_livechat.{mail,discuss}_channel_action_tree
        im_livechat.{mail,discuss}_channel_action
        im_livechat.{mail,discuss}_channel_view_form
        im_livechat.{mail,discuss}_channel_view_search
        im_livechat.{mail,discuss}_channel_view_tree
    """
    for rename in util.splitlines(xmlids):
        util.rename_xmlid(cr, *eb(rename))
    for num in range(8):
        util.rename_xmlid(cr, *eb(f"im_livechat.im_livechat_{{mail,discuss}}_channel_data_{num}"))
    util.rename_xmlid(cr, *eb("im_livechat.{mail,discuss}_channel_livechat_1"))
