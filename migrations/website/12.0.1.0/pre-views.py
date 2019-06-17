# -*- coding: utf-8 -*-
from functools import partial
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    force_update = partial(util.force_noupdate, noupdate=False)

    for view in {"homepage", "contactus", "aboutus"}:
        xid = "website." + view
        util.force_noupdate(cr, xid)
        util.if_unchanged(cr, xid, callback=force_update)
