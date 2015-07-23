# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""\
        WITH mail_followers_to_keep AS (
            SELECT min(id) AS id FROM mail_followers
                GROUP BY res_model, res_id, partner_id
        )
        DELETE FROM mail_followers WHERE NOT EXISTS (
            SELECT 1 FROM mail_followers_to_keep WHERE
                mail_followers_to_keep.id = mail_followers.id
        );
        """)
