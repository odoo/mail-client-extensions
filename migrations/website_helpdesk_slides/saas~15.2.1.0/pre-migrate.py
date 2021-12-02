# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "elearning_id")
    util.remove_field(cr, "helpdesk.team", "elearning_url")

    util.remove_view(cr, "website_helpdesk_slides.website_helpdesk_slides_team_page")
    util.remove_view(cr, "website_helpdesk_slides.slides_page")
