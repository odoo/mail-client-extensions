# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "website_slide_google_app_key")
    util.create_column(cr, "website", "website_slide_google_app_key", "varchar")
    util.create_column(cr, "slide_channel", "website_id", "int4")

    ICP = util.env(cr)["ir.config_parameter"]
    param_value = ICP.get_param("website_slides.google_app_key")
    if param_value:
        cr.execute("UPDATE website set website_slide_google_app_key=%s", (param_value,))
    util.remove_record(cr, "website_slides.google_app_key")

    util.if_unchanged(cr, "website_slides.slide_template_published", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.slide_template_shared", util.update_record_from_xml)
