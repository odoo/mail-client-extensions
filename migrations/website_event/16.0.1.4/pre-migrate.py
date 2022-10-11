# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.event_edit_options")
    util.remove_view(cr, "website_event.user_navbar_inherit_website_event")
