# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE calendar_contacts
           SET user_id = create_uid
         WHERE user_id IS NULL
    """)

    cr.execute("""
        WITH dupes AS (
            select min(id) as id,
                   (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)] as dupes,
                   bool_or(active) as active
              from calendar_contacts
          group by user_id, partner_id
            having count(id) > 1
        ),

        _up AS (
            UPDATE calendar_contacts c
               SET active = d.active
              FROM dupes d
             WHERE d.id = c.id
        )
        DELETE FROM calendar_contacts WHERE id IN (SELECT unnest(dupes) FROM dupes)
    """)
