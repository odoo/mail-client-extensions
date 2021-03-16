# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website.dynamic_snippet_country_filter")
    util.remove_record(cr, "website.dynamic_snippet_data_source_country")

    util.remove_view(cr, "website.dynamic_filter_template_image_title_footer")
    util.remove_view(cr, "website.dynamic_filter_template_header_image_footer_card")
