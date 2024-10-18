from odoo.upgrade.util import remove_view


def migrate(cr, version):
    remove_view(cr, "website.s_masonry_block_alternation_text_image_text_template")
    remove_view(cr, "website.s_masonry_block_alternation_text_template")
    remove_view(cr, "website.s_masonry_block_image_texts_image_template")
    remove_view(cr, "website.s_masonry_block_texts_image_texts_template")
