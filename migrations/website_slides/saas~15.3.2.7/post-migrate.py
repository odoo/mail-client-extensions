# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Link URLs have been updated in the following templates
    util.update_record_from_xml(cr, "website_slides.slide_template_published")
    util.update_record_from_xml(cr, "website_slides.slide_template_shared")
