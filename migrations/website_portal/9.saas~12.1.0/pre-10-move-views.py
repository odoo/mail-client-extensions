#!/usr/bin/env python
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "website_portal.account", "website_portal.portal_layout")
    util.force_noupdate(cr, "website_portal.portal_layout", False)  # Because it changed a lot.
