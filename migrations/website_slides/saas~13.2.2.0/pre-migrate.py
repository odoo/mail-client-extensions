# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "slide_answer", "comment", "text")
    util.create_column(cr, "slide_slide", "slide_resource_downloadable", "boolean")

    for model in "slide question answer tag channel slide_link".split():
        util.remove_record(cr, f"website_slide.access_slide_{model}_publisher")

    util.remove_record(cr, "website_slide.rule_slide_channel_website")
    util.remove_record(cr, "website_slide.rule_slide_slide_website")
