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
