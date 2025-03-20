from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    # Remove old discuss public view
    util.remove_view(cr, "mail.discuss_public_layout")

    util.explode_execute(
        cr,
        "UPDATE mail_message SET model='discuss.channel' WHERE model='mail.channel'",
        table="mail_message",
    )
    util.parallel_execute(
        cr,
        [
            "UPDATE ir_attachment SET res_model='discuss.channel' WHERE res_model='mail.channel'",
            # create a temporary partial index to speed up the update done by `rename_model`.
            # (this update being a no-op as we just updates `mail_message` above)
            "CREATE INDEX _tmp_upg_mm_mc ON mail_message(id) WHERE model='mail.channel'",
        ],
    )

    # Rename mail.channel to discuss.channel
    model_names = """
        {mail,discuss}.channel.member
        {mail,discuss}.channel.rtc.session
        {mail,discuss}.channel
    """
    for rename in util.splitlines(model_names):
        util.rename_model(cr, *eb(rename))
    xmlids = """
        mail.{mail_channel_,}ice_servers_menu
        mail.{mail,discuss}_channel_action_view
        mail.{mail,discuss}_channel_admin
        mail.{mail,discuss}_channel_integrations_menu
        mail.{mail,discuss}_channel_member_action
        mail.{mail,discuss}_channel_member_view_form
        mail.{mail,discuss}_channel_member_view_tree
        mail.{mail,discuss}_channel_menu_settings
        mail.{mail,discuss}_channel_rtc_session_action
        mail.{mail,discuss}_channel_rtc_session_menu
        mail.{mail,discuss}_channel_rtc_session_view_form
        mail.{mail,discuss}_channel_rtc_session_view_search
        mail.{mail,discuss}_channel_rtc_session_view_tree
        mail.{mail,discuss}_channel_rule
        mail.{mail,discuss}_channel_view_form
        mail.{mail,discuss}_channel_view_kanban
        mail.{mail,discuss}_channel_view_search
        mail.{mail,discuss}_channel_view_tree
        mail.ir_rule_{mail,discuss}_channel_member_group_system
        mail.ir_rule_{mail,discuss}_channel_member_group_user
        # access rules
        mail.access_{mail,discuss}_channel_all
        mail.access_{mail,discuss}_channel_user
        mail.access_{mail,discuss}_channel_admin
        mail.access_{mail,discuss}_channel_member_public
        mail.access_{mail,discuss}_channel_member_portal
        mail.access_{mail,discuss}_channel_member_user
        mail.access_{mail,discuss}_channel_rtc_session_all
        mail.access_{mail,discuss}_channel_rtc_session_system
        # menus
        mail.{mail,discuss}_channel_menu_settings
        mail.{mail,discuss}_channel_member_menu
    """
    for rename in util.splitlines(xmlids):
        util.rename_xmlid(cr, *eb(rename))
    index_names = """
        {mail,discuss}_channel_member_seen_message_id_idx
        {mail,discuss}_channel_member_guest_unique
    """
    for rename in util.splitlines(index_names):
        cr.execute(util.format_query(cr, "ALTER INDEX IF EXISTS {0} RENAME TO {1}", *eb(rename)))

    cr.execute("DROP INDEX _tmp_upg_mm_mc")
