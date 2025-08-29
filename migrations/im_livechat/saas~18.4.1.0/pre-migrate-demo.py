from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "im_livechat_channel_member_history"):
        return  # nosemgrep: no-early-return
    demo_history_guest = (
        [
            (
                f"im_livechat.livechat_channel_chatbot_session_{i}_history_guest_demo",
                f"im_livechat.livechat_channel_chatbot_session_{i}_demo",
                f"im_livechat.livechat_channel_chatbot_session_{i}_guest_demo",
            )
            for i in (1, 2, 3)
        ]
        + [
            (
                f"im_livechat.livechat_channel_session_{i}_history_guest",
                f"im_livechat.livechat_channel_session_{i}",
                f"im_livechat.livechat_channel_session_{i}_guest",
            )
            for i in (1, 2)
        ]
        + [
            (
                f"im_livechat.livechat_channel_session_{i}_history_member_guest",
                f"im_livechat.livechat_channel_session_{i}",
                f"im_livechat.livechat_channel_session_{i}_guest",
            )
            for i in (5, 6, 8, 9, 10, 11, 12, 13, 14)
        ]
        + [
            (
                f"im_livechat.support_bot_session_{i}_history_member_guest_demo",
                f"im_livechat.support_bot_session_{i}_demo",
                f"im_livechat.support_bot_session_{i}_guest_demo",
            )
            for i in range(1, 8)
        ]
    )

    demo_history_partner = (
        [
            (
                f"im_livechat.livechat_channel_session_{i}_history_member_admin",
                f"im_livechat.livechat_channel_session_{i}",
                "base.partner_admin",
            )
            for i in (1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14)
        ]
        + [
            (
                f"im_livechat.livechat_channel_session_{i}_history_member_demo",
                f"im_livechat.livechat_channel_session_{i}",
                "base.partner_demo",
            )
            for i in (2, 4, 8, 14)
        ]
        + [
            (
                f"im_livechat.livechat_channel_session_{i}_history_member_portal",
                f"im_livechat.livechat_channel_session_{i}",
                "base.partner_demo_portal",
            )
            for i in (3, 4, 7)
        ]
        + [
            (
                f"im_livechat.support_bot_session_{i}_member_history_admin",
                f"im_livechat.support_bot_session_{i}_demo",
                "base.partner_admin",
            )
            for i in (1, 4, 6)
        ]
    )

    for history_xid, channel_xid, guest_xid in demo_history_guest:
        channel_id = util.ref(cr, channel_xid)
        guest_id = util.ref(cr, guest_xid)
        if channel_id and guest_id:
            util.ensure_xmlid_match_record(
                cr,
                history_xid,
                "im_livechat.channel.member.history",
                {"channel_id": channel_id, "guest_id": guest_id},
            )

    for history_xid, channel_xid, partner_xid in demo_history_partner:
        channel_id = util.ref(cr, channel_xid)
        partner_id = util.ref(cr, partner_xid)
        if channel_id and partner_id:
            util.ensure_xmlid_match_record(
                cr,
                history_xid,
                "im_livechat.channel.member.history",
                {"channel_id": channel_id, "partner_id": partner_id},
            )
