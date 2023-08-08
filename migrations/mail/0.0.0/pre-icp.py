# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # some customers remove and recreate data ICP.
    if util.version_between("saas~14.5", "saas~16.4"):
        # already handled in `base`
        return
    util.import_script("base/0.0.0/pre-mail-icp.py").match(cr, "mail")
