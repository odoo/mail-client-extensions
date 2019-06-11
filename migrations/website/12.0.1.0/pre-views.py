# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for view in {"homepage", "contactus", "aboutus"}:
        util.force_noupdate(cr, "website." + view, False)
