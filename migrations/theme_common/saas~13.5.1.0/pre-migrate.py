# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "theme_common.snippets")
    util.remove_record(cr, "theme_common.s_google_map")
    util.remove_record(cr, "theme_common.s_google_map_option")
    util.remove_record(cr, "theme_common.s_animated_boxes_options")
    util.remove_record(cr, "theme_common.s_badge")
    util.remove_record(cr, "theme_common.s_badge_options")
    util.remove_record(cr, "theme_common.s_clonable_boxes-opt")
    util.remove_record(cr, "theme_common.s_color_blocks_2-opt")
    util.remove_record(cr, "theme_common.s_color_blocks_4-opt")
    util.remove_record(cr, "theme_common.s_css_slider_options")
    util.remove_record(cr, "theme_common.s_discount_opt")
    util.remove_record(cr, "theme_common.s_event_list-opt")
    util.remove_record(cr, "theme_common.s_features_carousel-opt")
    util.remove_record(cr, "theme_common.s_images_carousel_options")
    util.remove_record(cr, "theme_common.s_images_row_options")
    util.remove_record(cr, "theme_common.s_masonry_block-opt")
    util.remove_record(cr, "theme_common.s_news_carousel_options")
    util.remove_record(cr, "theme_common.s_showcase-opt")
    util.remove_record(cr, "theme_common.s_showcase_image-opt")
    util.remove_record(cr, "theme_common.s_showcase_slider_options")
    util.remove_record(cr, "theme_common.s_text_highlight-opt")
