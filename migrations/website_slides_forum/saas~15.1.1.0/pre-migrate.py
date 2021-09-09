# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_slides_forum.forum_post_action_report")
    util.remove_menus(cr, [util.ref(cr, "website_slides_forum.website_slides_menu_report_forum")])
