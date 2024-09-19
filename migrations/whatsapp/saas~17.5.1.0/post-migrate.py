from odoo.upgrade import util


def migrate(cr, version):
    query = """
        WITH channel_latest_message AS (
            SELECT c.id AS cid, MAX(m.id) as mid
              FROM discuss_channel c
              JOIN mail_message m
                ON m.res_id = c.id
               AND m.author_id = c.whatsapp_partner_id
             WHERE c.channel_type = 'whatsapp'
               AND m.model = 'discuss.channel'
               AND {parallel_filter}
          GROUP BY c.id
        )
        UPDATE discuss_channel c
           SET last_wa_mail_message_id = lm.mid
          FROM channel_latest_message lm
         WHERE c.id = lm.cid
    """
    util.explode_execute(cr, query, table="discuss_channel", alias="c")
