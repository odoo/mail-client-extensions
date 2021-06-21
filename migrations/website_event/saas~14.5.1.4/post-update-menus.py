# -*- coding: utf-8 -*-


def migrate(cr, version):
    # create website.event.menu for introduction/location/register that were not using that mechanism
    cr.execute(
        """
        WITH wmenus AS (
            SELECT event.id as ev_id,
                   wmenu.id as wm_id,
                   CASE WHEN SPLIT_PART(url, '/', 4) = 'register' THEN 'register'
                        WHEN SPLIT_PART(SPLIT_PART(url, '/', 5), '-', 1) = 'introduction' THEN 'introduction'
                        WHEN SPLIT_PART(SPLIT_PART(url, '/', 5), '-', 1) = 'location' THEN 'location'
                   END wm_type,
                   SPLIT_PART(url, '/', 5) as wm_view_name
              FROM event_event event
              JOIN website_menu wmenu ON (wmenu.parent_id = event.menu_id)
             WHERE event.website_menu is true
        )

        INSERT INTO website_event_menu(event_id, menu_id, view_id, menu_type)
             SELECT wmenus.ev_id, wmenus.wm_id, view.id, wmenus.wm_type
               FROM wmenus
          LEFT JOIN ir_ui_view view ON (view.key = 'website_event.' || wmenus.wm_view_name)
              WHERE wmenus.wm_type IS NOT NULL;
    """
    )

    # update computed / editable fields based on created menus
    cr.execute(
        """
        WITH wemenus AS (
            SELECT event_id, array_agg(menu_type) as types
              FROM website_event_menu
          GROUP BY event_id
        )
        UPDATE event_event event
           SET introduction_menu = wemenus.types && ARRAY['introduction']::varchar[],
               location_menu = wemenus.types && ARRAY['location']::varchar[],
               register_menu = wemenus.types && ARRAY['register']::varchar[]
          FROM wemenus
         WHERE wemenus.event_id = event.id
    """
    )
