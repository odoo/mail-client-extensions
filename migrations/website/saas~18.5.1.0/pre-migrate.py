from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website.new_page_template_gallery_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_0_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_1_s_text_block_h2")
    util.remove_view(cr, "website.new_page_template_gallery_3_s_text_block_h2")
