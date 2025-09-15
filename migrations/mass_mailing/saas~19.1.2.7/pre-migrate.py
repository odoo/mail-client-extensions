from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.s_masonry_block_alternation_text_image_text_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_alternation_image_text_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_alternation_text_image_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_alternation_text_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_texts_image_texts_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_mosaic_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_image_texts_image_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_images_template")
    util.remove_view(cr, "mass_mailing.s_masonry_block_reversed_template")
