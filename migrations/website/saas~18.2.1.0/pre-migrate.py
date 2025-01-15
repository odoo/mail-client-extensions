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
