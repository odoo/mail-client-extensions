from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE discuss_channel
           SET livechat_active = false
         WHERE livechat_active IS NOT false
        """,
        table="discuss_channel",
    )
    util.explode_execute(
        cr,
        """
        UPDATE discuss_channel_member m
           SET is_pinned = false
          FROM discuss_channel c
         WHERE c.id = m.channel_id
           AND c.channel_type = 'livechat'
           AND m.is_pinned IS NOT false
        """,
        table="discuss_channel_member",
        alias="m",
    )

    # move livechat_username from res_users to res_users_settings
    util.create_column(cr, "res_users_settings", "livechat_username", "varchar")
    extra_cols = extra_vals = extra_cnfl = util.SQLStr("")
    if util.column_exists(cr, "res_users_settings", "how_to_call_on_mobile"):
        # If VOIP is installed, set the required field 'how_to_call_on_mobile' to 'ask' as default
        extra_cols = util.ColumnList.from_unquoted(cr, ["how_to_call_on_mobile"]).using(leading_comma=True)
        extra_vals = util.SQLStr(", 'ask'")
        extra_cnfl = util.format_query(cr, ", {0} = EXCLUDED.{0}", "how_to_call_on_mobile")
    # update res_users_settings with livechat_username from res_users
    # create res_users_settings for users that don't have one
    query = util.format_query(
        cr,
        """
        INSERT INTO res_users_settings (user_id, livechat_username {})
             SELECT u.id, u.livechat_username {}
               FROM res_users u
              WHERE u.livechat_username IS NOT NULL
                AND {{parallel_filter}}
        ON CONFLICT (user_id) DO UPDATE
                SET livechat_username = EXCLUDED.livechat_username
                    {}
        """,
        extra_cols,
        extra_vals,
        extra_cnfl,
    )
    util.explode_execute(cr, query, table="res_users", alias="u")

    # remove livechat_username from res_users
    util.remove_column(cr, "res_users", "livechat_username")

    # channel ACL simplification
    util.remove_record(cr, "im_livechat.im_livechat_rule_manager_read_all_discuss_channel")
