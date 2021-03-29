# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website.dynamic_snippet_country_filter")
    util.remove_record(cr, "website.dynamic_snippet_data_source_country")

    util.remove_view(cr, "website.dynamic_filter_template_image_title_footer")
    util.remove_view(cr, "website.dynamic_filter_template_header_image_footer_card")
    util.remove_view(cr, "website.onboarding_website_theme_step")

    util.remove_field(cr, "res.company", "website_theme_onboarding_done")

    util.create_column(cr, "website", "configurator_done", "boolean")
