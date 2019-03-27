# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("website_event.{event_script,assets_frontend}"))
    util.remove_view(cr, "website_event.index")
