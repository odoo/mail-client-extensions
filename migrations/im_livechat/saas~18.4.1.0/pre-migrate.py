from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "im_livechat_channel", "max_sessions_mode"):
        util.create_column(cr, "im_livechat_channel", "block_assignment_during_call", "boolean")
        cr.execute("""
          UPDATE im_livechat_channel
             SET block_assignment_during_call = True
           WHERE max_sessions_mode = 'limited'
        """)
    if util.table_exists(cr, "im_livechat_channel_member_history"):
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
