# -*- coding: utf-8 -*-

def migrate(cr, version):
    # NOTE: computation done on url as name is translatable (and more likely to be changed)
    cr.execute("""
        WITH menu_tails AS (
            SELECT e.id as eid,
                   m.id as mid,
                   (regexp_split_to_array(m.url, '/'))[array_length(regexp_split_to_array(m.url, '/'), 1)] as tail
              FROM event_event e
         LEFT JOIN website_menu m ON (e.menu_id = m.parent_id)
        )

        INSERT INTO website_event_menu(event_id, menu_id, menu_type)
             SELECT eid, mid,
                    CASE WHEN tail = 'track_proposal' THEN 'track_proposal'
                         ELSE 'track'
                     END
                FROM menu_tails
               WHERE tail IN ('track', 'agenda', 'track_proposal')
    """)

    cr.execute("""
        WITH mt AS (
            SELECT event_id, array_agg(menu_type) as types
              FROM website_event_menu
          GROUP BY event_id
        )
        UPDATE event_event e
           SET website_track = mt.types && ARRAY['track']::varchar[],
               website_track_proposal = mt.types && ARRAY['track_proposal']::varchar[]
          FROM mt
         WHERE mt.event_id = e.id
    """)
