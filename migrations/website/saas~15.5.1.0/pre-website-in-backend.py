# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website.action_website_pages_list")
    util.remove_view(cr, "website.list_website_pages")
    util.remove_view(cr, "website.one_page_line")
    util.remove_view(cr, "website.publish_short")
    util.remove_view(cr, "website.index_management")
    util.remove_view(cr, "website.user_navbar")
    util.remove_view(cr, "website.website_configurator")
    util.remove_view(cr, "website.website_publisher")
