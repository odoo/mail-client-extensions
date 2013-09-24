# -*- coding: utf-8 -*-

def migrate(cr, version):
    # deduplicate users
    cr.execute("""
        WITH duplicates(i, d) AS (
                SELECT min(u.id), array_agg(u.id)
                  FROM im_user u
                 WHERE u.user IS NOT NULL
              GROUP BY u.user
                HAVING count(u.id) > 1
        )
        UPDATE im_message m
           SET from_id = CASE WHEN m.from_id = ANY(d.d) THEN d.i ELSE m.from_id END,
               to_id = CASE WHEN m.to_id = ANY(d.d) THEN d.i ELSE m.to_id END
          FROM duplicates d
         WHERE ARRAY[m.from_id, m.to_id] && d.d
    """)

    # delete duplicated im_users
    cr.execute("""
        DELETE FROM im_user u
              WHERE u.user IS NOT NULL
                AND EXISTS(SELECT 1
                             FROM im_user u2
                            WHERE u2.user = u.user
                              AND u2.id < u.id)
    """)
