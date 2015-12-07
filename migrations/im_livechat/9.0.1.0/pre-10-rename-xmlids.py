# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    cr.execute("DROP VIEW IF EXISTS im_livechat_report")

    util.remove_record(cr, 'im_livechat.action_client_livechat_menu')
    renames = {
        'im_livechat_rating_0': ('mail_shortcode_rating_0', False),
        'im_livechat_rating_5': ('mail_shortcode_rating_5', False),
        'im_livechat_rating_10': ('mail_shortcode_rating_10', False),

        'channel_website': ('im_livechat_channel_demo', False),
        'channel_rule': ('im_livechat_channel_rule_demo', False),

        'group_im_livechat': ('im_livechat_group_user', True),
        'group_im_livechat_manager': ('im_livechat_group_manager', True),
        'message_rule_1': ('mail_message_rule_manager', True),
        'session_rule_1': ('mail_channel_rule_manager', True),

        'access_ls_chann1': ('access_livechat_channel', False),
        'access_ls_chann2': ('access_livechat_channel_user', False),
        'access_ls_chann3': ('access_livechat_channel_manager', False),

        'access_ls_chann_rule1': ('access_livechat_channel_rule', False),
        'access_ls_chann_rule2': ('access_livechat_channel_rule_user', False),
        'access_ls_chann_rule3': ('access_livechat_channel_rule_manager', False),
    }

    for old, (new, upd) in renames.iteritems():
        util.rename_xmlid(cr, 'im_livechat.' + old, 'im_livechat.' + new)
        if upd:
            util.force_noupdate(cr, 'im_livechat.' + new, False)
