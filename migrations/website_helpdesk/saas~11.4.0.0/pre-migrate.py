# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #deprectated view
    util.remove_view(cr, "website_helpdesk.content_new_team")
