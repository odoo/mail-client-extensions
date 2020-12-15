# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "slide_channel", "completed_template_id", "int4")
    util.remove_record(cr, "website_slides.slide_channel_partner_action")
