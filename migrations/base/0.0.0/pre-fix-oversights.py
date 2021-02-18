# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("10.saas~18"):
        # Should have been removed in saas~18...
        util.remove_constraint(cr, "res_partner_title", "res_partner_title_name_uniq")
