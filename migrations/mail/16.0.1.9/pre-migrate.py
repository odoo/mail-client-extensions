from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "mail.channel.partner", "mail.channel.member")
    util.rename_field(cr, "mail.channel.rtc.session", "channel_partner_id", "channel_member_id")
    util.rename_field(cr, "mail.channel", "channel_last_seen_partner_ids", "channel_member_ids")

    eb = util.expand_braces
    renames = """
        mail.channel_{partner,member}_general_channel_for_admin
        mail.mail_channel_{partner,member}_view_tree
        mail.mail_channel_{partner,member}_view_form
        mail.mail_channel_{partner,member}_action
        mail.mail_channel_{partner,member}_menu

        mail.ir_rule_mail_channel_{partner,member}_group_user
        mail.ir_rule_mail_channel_{partner,member}_group_system

        mail.access_mail_channel_{partner,member}_public
        mail.access_mail_channel_{partner,member}_portal
        mail.access_mail_channel_{partner,member}_user
    """
    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(rename))

    indexes = """
        mail_channel_{partner,member}_guest_unique
        mail_channel_{partner,member}_partner_unique
        mail_channel_{partner,member}_seen_message_id_idx
        mail_channel_rtc_session_channel_{partner,member}_unique
    """
    for old, new in map(eb, util.splitlines(indexes)):
        cr.execute(util.format_query(cr, "ALTER INDEX IF EXISTS {} RENAME TO {}", old, new))
