# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "website_slides.action_slide_channels")
    util.remove_view(cr, "website_slides.view_slide_question_form")
    util.remove_view(cr, "website_slides.view_slide_slide_graph")  # diffrent that the new one
    util.remove_record(cr, "website_slides.action_slides_slides")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "website_slides." + menu)
            for menu in util.splitlines(
                """
                    menu_website_slides_root
                    menu_website_slides_root_global
                    menu_action_slide_channels_global
                    menu_action_ir_slide_category_global

                    menu_slide_tag
                    slide_channel_tag_menu
                    slide_channel_tag_group_menu
                """
            )
        ],
    )
