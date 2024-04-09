from odoo.upgrade.util import remove_record


def migrate(cr, version):
    remove_record(cr, "website.s_chart_000_js")
    remove_record(cr, "website.s_countdown_000_js")
    remove_record(cr, "website.s_dynamic_snippet_000_js")
    remove_record(cr, "website.s_dynamic_snippet_carousel_000_js")
    remove_record(cr, "website.s_embed_code_000_js")
    remove_record(cr, "website.s_facebook_page_000_js")
    remove_record(cr, "website.s_faq_horizontal_000_js")
    remove_record(cr, "website.s_google_map_000_js")
    remove_record(cr, "website.s_image_gallery_000_js")
    remove_record(cr, "website.s_instagram_page_000_js")
    remove_record(cr, "website.s_map_000_js")
    remove_record(cr, "website.s_popup_000_js")
    remove_record(cr, "website.s_searchbar_000_js")
    remove_record(cr, "website.s_share_000_js")
    remove_record(cr, "website.s_table_of_content_000_js")
    remove_record(cr, "website.s_website_form_000_js")

    cr.execute(
        """
        WITH info AS (
                SELECT wm.id,
                       wp.url AS page_url,
                       wm.url AS menu_url,
                       wm.mega_menu_content IS NOT NULL AS is_mega,
                       count(child.id) > 0 AS has_child
                  FROM website_menu wm
             LEFT JOIN website_menu child
                    ON child.parent_id = wm.id
             LEFT JOIN website_page wp
                    ON wm.page_id = wp.id
                 GROUP BY wm.id, wp.url
            )
            UPDATE website_menu AS wm
               SET url = CASE
                             WHEN info.is_mega OR info.has_child THEN '#'
                             WHEN info.page_url IS NOT NULL AND info.page_url != '' THEN info.page_url
                             WHEN info.menu_url IS NOT NULL AND info.menu_url != '' THEN info.menu_url
                             ELSE '#'
                         END
              FROM info
             WHERE info.id = wm.id
        """
    )
