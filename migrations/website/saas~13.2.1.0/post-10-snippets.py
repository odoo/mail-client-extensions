# -*- coding: utf-8 -*-
import odoo.upgrade.util.snippets as snip


def migrate(cr, version):
    snippets = [
        snip.Snippet("s_alert"),
        snip.Snippet("s_animated_boxes"),
        snip.Snippet("s_badge"),
        snip.Snippet("s_banner"),
        snip.Snippet("s_banner_parallax"),
        snip.Snippet("s_big_icons"),
        snip.Snippet("s_big_image"),
        snip.Snippet("s_big_image_parallax"),
        snip.Snippet("s_blockquote"),
        snip.Snippet("s_btn"),
        snip.Snippet("s_call_to_action"),
        snip.Snippet("s_card"),
        snip.Snippet("s_carousel"),
        snip.Snippet("s_carousel", "section", "s_carousel_wrapper"),
        snip.Snippet("s_chart"),
        snip.Snippet("s_clonable_boxes"),
        snip.Snippet("s_column"),
        snip.Snippet("s_color_blocks_2"),
        snip.Snippet("s_color_blocks_4"),
        snip.Snippet("s_color_blocks_img"),
        snip.Snippet("s_compact_menu"),
        snip.Snippet("s_company_team"),
        snip.Snippet("s_comparisons"),
        snip.Snippet("s_countdown"),
        snip.Snippet("s_cover"),
        snip.Snippet("s_css_slider"),
        snip.Snippet("s_discount"),
        snip.Snippet("s_event_list"),
        snip.Snippet("s_event_slide"),
        snip.Snippet("s_facebook_page", "div", "o_facebook_page"),
        snip.Snippet("s_faq_collapse"),
        snip.Snippet("s_features"),
        snip.Snippet("s_features_grid"),
        snip.Snippet("s_features_carousel"),
        snip.Snippet("s_full_menu"),
        snip.Snippet("s_google_map"),
        snip.Snippet("s_header_text_big_picture"),
        snip.Snippet("s_hr"),
        snip.Snippet("s_icon_box"),
        snip.Snippet("s_image_gallery"),
        snip.Snippet("s_images_carousel"),
        snip.Snippet("s_images_row"),
        # s_image_text has same selector and same behaviour as s_text_image.
        snip.Snippet("s_masonry_block"),
        snip.Snippet("s_media_list"),
        snip.Snippet("s_mega_menu_menu_image_menu"),
        snip.Snippet("s_mega_menu_multi_menus"),
        snip.Snippet("s_menu_three_columns"),
        snip.Snippet("s_mini_nav_bar"),
        snip.Snippet("s_news_carousel"),
        snip.Snippet("s_numbers"),
        snip.Snippet("s_page_header"),
        snip.Snippet("s_parallax"),
        snip.Snippet("s_picture"),
        snip.Snippet("s_popup"),
        snip.Snippet("s_pricing"),
        snip.Snippet("s_process_steps"),
        snip.Snippet("s_products_carousel"),
        snip.Snippet("s_product_catalog"),
        snip.Snippet("s_product_list"),
        snip.Snippet("s_profile"),
        snip.Snippet("s_progress"),
        snip.Snippet("s_progress_bar"),
        snip.Snippet("s_quotes_carousel"),
        snip.Snippet("s_quotes_carousel", "section", "s_quotes_carousel_wrapper"),
        snip.Snippet("s_rating"),
        snip.Snippet("s_references"),
        snip.Snippet("s_separator_nav"),
        snip.Snippet("s_share"),
        snip.Snippet("s_showcase"),
        snip.Snippet("s_showcase_image"),
        snip.Snippet("s_showcase_slider"),
        snip.Snippet("s_table_of_content"),
        snip.Snippet("s_tabs"),
        snip.Snippet("s_team_profiles"),
        snip.Snippet("s_text_block"),
        snip.Snippet("s_text_highlight"),
        snip.Snippet("s_text_image"),
        snip.Snippet("s_text_picture_text"),
        snip.Snippet("s_three_columns"),
        snip.Snippet("s_three_columns_circle"),
        snip.Snippet("s_timeline"),
        snip.Snippet("s_title"),
        snip.Snippet("s_two_columns"),
        # website_form
        snip.Snippet("s_website_form"),
        # website_sale
        snip.Snippet("s_products_recently_viewed", "section", "s_wsale_products_recently_viewed"),
        snip.Snippet("s_products_searchbar", "section", "s_wsale_products_searchbar"),
        snip.Snippet("s_products_searchbar_input", "form", "s_wsale_products_searchbar_input"),
        # website_mass_mailing
        snip.Snippet("s_newsletter_block"),
        snip.Snippet("s_newsletter_subscribe_form"),
        snip.Snippet("s_newsletter_subscribe_popup", "div", "o_newsletter_popup"),
        snip.Snippet("s_newsletter_subscribe_form", "div", 'data-name="Newsletter"', '//div[@data-name="Newsletter"]'),
        # website_event
        snip.Snippet("s_country_events", "div", "s_country_events_list"),
        snip.Snippet("s_speaker_bio"),
        # website_blog
        snip.Snippet("s_latest_posts"),
        snip.Snippet("s_latest_posts_big_picture"),
        # website_mail_channel
        snip.Snippet("s_channel"),
        # website_twitter
        snip.Snippet("s_twitter", "section", "twitter_timeline", '//section[hasclass("twitter")]'),
    ]

    regex = snip.get_regex_from_snippets_list(snippets)

    # Add the snippet name on all snippets located in a website page
    select_query = cr.mogrify(
        """
            SELECT id, array((SELECT regexp_matches(arch_db, %(regex)s, 'g'))), arch_db
              FROM ir_ui_view
             WHERE website_id IS NOT NULL
               AND arch_db ~ %(regex)s
        """,
        dict(regex=regex),
    )
    snip.add_snippet_names(cr, "ir_ui_view", "arch_db", snippets, select_query)

    # Add the snippet name on all snippets located in an html field
    for table, column in snip.get_html_fields(cr):
        snip.add_snippet_names_on_html_field(cr, table, column, snippets, regex)
