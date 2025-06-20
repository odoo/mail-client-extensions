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
