# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # unused view
    util.remove_view(cr, "website_event_booth_exhibitor.event_booth_view_search")
