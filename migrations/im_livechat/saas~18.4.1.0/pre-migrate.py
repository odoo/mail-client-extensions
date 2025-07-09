from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "im_livechat_channel", "max_sessions_mode"):
        util.create_column(cr, "im_livechat_channel", "block_assignment_during_call", "boolean")
        cr.execute("""
          UPDATE im_livechat_channel
             SET block_assignment_during_call = True
           WHERE max_sessions_mode = 'limited'
        """)

    def domain_adapter(leaf, _, __):
        _, operator, right = leaf
        right = (operator == "=" and not right) or (operator == "!=" and right)
        return [("livechat_end_dt", "!=" if right else "=", False)]

    util.update_field_usage(cr, "discuss.channel", "livechat_active", "livechat_end_dt", domain_adapter=domain_adapter)
    util.create_column(cr, "discuss_channel", "livechat_end_dt", "timestamp without time zone")
    query = """
        WITH end_dt_by_channel AS (
          SELECT discuss_channel.id as channel_id,
                 COALESCE(max(mail_message.create_date), discuss_channel.write_date) AS end_dt
            FROM discuss_channel
       LEFT JOIN mail_message
              ON mail_message.model = 'discuss.channel'
             AND mail_message.res_id = discuss_channel.id
           WHERE {parallel_filter}
             AND discuss_channel.channel_type = 'livechat'
             AND discuss_channel.livechat_active IS NOT TRUE
        GROUP BY discuss_channel.id
        )
        UPDATE discuss_channel
           SET livechat_end_dt = end_dt_by_channel.end_dt
          FROM end_dt_by_channel
         WHERE discuss_channel.id = end_dt_by_channel.channel_id
    """
    util.explode_execute(cr, query, "discuss_channel")
    util.remove_field(cr, "discuss.channel", "livechat_active")

    util.create_column(cr, "discuss_channel", "livechat_start_hour", "float")
    util.create_column(cr, "discuss_channel", "livechat_week_day", "varchar")
    query = """
      UPDATE discuss_channel
         SET livechat_start_hour = EXTRACT(HOUR FROM discuss_channel.create_date),
             livechat_week_day = MOD(EXTRACT(DOW from discuss_channel.create_date)::int + 6, 7)
       WHERE discuss_channel.channel_type = 'livechat'
    """
    util.explode_execute(cr, query, "discuss_channel")
    util.create_column(cr, "discuss_channel", "livechat_outcome", "varchar")
    util.create_column(cr, "discuss_channel", "livechat_agent_requesting_help_history", "int4")
    util.create_column(cr, "discuss_channel", "livechat_agent_providing_help_history", "int4")
    util.create_column(cr, "discuss_channel", "rating_last_text", "varchar")
    query = """
        WITH last_ratings AS (
            SELECT c.id,
                   (ARRAY_AGG(r.rating_text ORDER BY r.write_date desc, r.id desc))[1] rating_text
              FROM rating_rating r
              JOIN discuss_channel c
                ON c.id = r.res_id
               AND r.res_model = 'discuss.channel'
             WHERE channel_type = 'livechat'
               AND {parallel_filter}
          GROUP BY c.id
        )
        UPDATE discuss_channel c
           SET rating_last_text = l.rating_text
          FROM last_ratings l
         WHERE c.id = l.id
    """
    util.explode_execute(cr, query, table="discuss_channel", alias="c")
    if util.column_exists(cr, "discuss_channel", "livechat_failure"):
        query = """
          UPDATE discuss_channel
             SET livechat_outcome =
                     CASE
                         WHEN livechat_is_escalated THEN 'escalated'
                         ELSE livechat_failure
                      END
           WHERE channel_type = 'livechat'
        """
        util.explode_execute(cr, query, "discuss_channel")
    if util.table_exists(cr, "im_livechat_channel_member_history"):
        util.create_column(cr, "im_livechat_channel_member_history", "message_count", "int4")
        util.create_column(cr, "im_livechat_channel_member_history", "rating_id", "int4")
        util.create_column(cr, "im_livechat_channel_member_history", "session_duration_hour", "float")
        util.create_column(cr, "im_livechat_channel_member_history", "help_status", "varchar")
        util.create_column(cr, "im_livechat_channel_member_history", "has_call", "float")
        util.create_column(cr, "im_livechat_channel_member_history", "call_duration_hour", "float")
        query = """
          WITH duplicated_history_data AS (
            SELECT ARRAY_AGG(history.id ORDER BY history.id) AS ids
              FROM discuss_channel
              JOIN im_livechat_channel_member_history history
                ON discuss_channel.id = history.channel_id
             WHERE partner_id IS NOT NULL
               AND {parallel_filter}
          GROUP BY history.channel_id,
                  history.partner_id
            HAVING COUNT(*) > 1
          ),
          _deleted AS (
            DELETE FROM im_livechat_channel_member_history history
             USING duplicated_history_data dups
             WHERE history.id = ANY(dups.ids[1:ARRAY_LENGTH(dups.ids, 1) - 1])
          )
          UPDATE im_livechat_channel_member_history last_history
             SET create_date = first_history.create_date
            FROM duplicated_history_data dups
            JOIN im_livechat_channel_member_history first_history
              ON first_history.id = dups.ids[1]
           WHERE last_history.id = dups.ids[ARRAY_LENGTH(dups.ids, 1)]
        """
        util.explode_execute(cr, query, "discuss_channel")
        query = """
          WITH agent_histories AS (
            SELECT discuss_channel.id AS channel_id,
                   (ARRAY_AGG(h.id ORDER BY h.create_date, h.id))[1] AS first_id,
                   (ARRAY_AGG(h.id ORDER BY h.create_date desc, h.id desc))[1] AS last_id
              FROM discuss_channel
              JOIN im_livechat_channel_member_history h
                ON h.channel_id = discuss_channel.id
               AND h.livechat_member_type = 'agent'
             WHERE discuss_channel.livechat_is_escalated
          GROUP BY discuss_channel.id
          )
          UPDATE discuss_channel
             SET livechat_agent_requesting_help_history = agent_histories.first_id,
                 livechat_agent_providing_help_history = agent_histories.last_id
            FROM agent_histories
           WHERE discuss_channel.id = agent_histories.channel_id
        """
        util.explode_execute(cr, query, "discuss_channel")
        query = """
          WITH last_msg_dt_by_channel AS (
            SELECT discuss_channel.id AS channel_id,
                   COALESCE(discuss_channel.livechat_end_dt, MAX(mail_message.create_date), NOW()) AS dt
              FROM discuss_channel
         LEFT JOIN mail_message
                ON mail_message.res_id = discuss_channel.id
               AND mail_message.model = 'discuss.channel'
             WHERE {parallel_filter}
          GROUP BY discuss_channel.id
          )
          UPDATE im_livechat_channel_member_history history
             SET session_duration_hour = EXTRACT(EPOCH FROM (last_msg_dt_by_channel.dt) - history.create_date) / 3600
            FROM last_msg_dt_by_channel
           WHERE last_msg_dt_by_channel.channel_id = history.channel_id
        """
        util.explode_execute(cr, query, "discuss_channel")
        query = """
          UPDATE im_livechat_channel_member_history history
             SET help_status =
                CASE
                    WHEN discuss_channel.livechat_agent_requesting_help_history = history.id THEN 'requested'
                    WHEN discuss_channel.livechat_agent_providing_help_history = history.id THEN 'provided'
                    ELSE 'none'
                END
            FROM discuss_channel
           WHERE history.channel_id = discuss_channel.id
        """
        util.explode_execute(cr, query, "im_livechat_channel_member_history", alias="history")
        query = """
          WITH msg_count_by_history AS (
            SELECT count(*) AS count_,
                   history.id AS history_id
              FROM im_livechat_channel_member_history history
              JOIN mail_message
                ON mail_message.res_id = history.channel_id
               AND mail_message.model = 'discuss.channel'
               AND mail_message.message_type NOT IN ('notification', 'user_notification')
               AND (history.partner_id = mail_message.author_id OR history.guest_id = mail_message.author_guest_id)
             WHERE {parallel_filter}
          GROUP BY history.id
          )
          UPDATE im_livechat_channel_member_history history
             SET message_count = msg_count_by_history.count_
            FROM msg_count_by_history
           WHERE msg_count_by_history.history_id = history.id
        """
        util.explode_execute(cr, query, "im_livechat_channel_member_history", alias="history")
        query = """
          WITH rating_by_history AS (
            SELECT history.id AS history_id,
                   MAX(rating.id) AS rating_id
              FROM im_livechat_channel_member_history history
              JOIN rating_rating rating
                ON rating.res_id = history.channel_id
               AND rating.res_model = 'discuss.channel'
               AND rating.rated_partner_id = history.partner_id
             WHERE history.livechat_member_type IN ('agent', 'bot')
               AND {parallel_filter}
          GROUP BY history.id
          )
          UPDATE im_livechat_channel_member_history history
             SET rating_id = rating_by_history.rating_id
            FROM rating_by_history
           WHERE history.id = rating_by_history.history_id
        """
        util.explode_execute(cr, query, "im_livechat_channel_member_history", alias="history")

    util.rename_xmlid(cr, "im_livechat.menu_reporting_livechat_operator", "im_livechat.menu_reporting_livechat_agent")
    util.rename_xmlid(
        cr, "im_livechat.im_livechat_report_operator_action", "im_livechat.im_livechat_agent_history_action"
    )
