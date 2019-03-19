# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "portal._assets_frontend_helpers", False)
    util.force_noupdate(cr, "portal.assets_frontend", False)
    util.remove_view(cr, "portal.assets_common")
    util.force_noupdate(cr, "portal.signature_form", False)
