from odoo.upgrade import util
from odoo.upgrade.util import snippets


def fix_data_shape(el):
    if el.attrib["data-shape"].startswith("web_editor/"):
        el.attrib["data-shape"] = el.attrib["data-shape"].replace("web_editor/", "html_builder/", 1)
        return True
    return False


def migrate(cr, version):
    util.remove_view(cr, "website.new_page_template_gallery_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_0_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_1_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_3_s_text_block_h2")

    snippets.convert_html_content(
        cr,
        snippets.html_converter(fix_data_shape, selector="//img[@data-shape]"),
        where_column=r"~ '\ydata-shape=\"'",
    )

    util.remove_view(cr, "website.dynamic_snippet_carousel_options_template")
    util.remove_view(cr, "website.s_dynamic_snippet_options_template")
    util.remove_view(cr, "website.s_blockquote_options")
    util.remove_view(cr, "website.s_pricelist_cafe_add_product_widget")
    util.remove_view(cr, "website.s_pricelist_boxed_add_product_widget")
    util.remove_view(cr, "website.s_product_catalog_add_product_widget")
    util.remove_view(cr, "website.s_card_options")
    util.remove_view(cr, "website.snippet_options")
    util.remove_view(cr, "website.vertical_alignment_option")
    util.remove_view(cr, "website.grid_layout_options")
    util.remove_view(cr, "website.column_count_option")
    util.remove_view(cr, "website.snippet_options_conditional_visibility")
    util.remove_view(cr, "website.snippet_options_header_box")
    util.remove_view(cr, "website.snippet_options_shadow_widgets")
    util.remove_view(cr, "website.snippet_options_border_widgets")
    util.remove_view(cr, "website.snippet_options_border_line_widgets")
    util.remove_view(cr, "website.snippet_options_carousel")
    util.remove_view(cr, "website.snippet_options_tabs")
    util.remove_view(cr, "website.snippet_options_background_options")

    util.remove_field(cr, "res.config.settings", "module_marketing_automation")
