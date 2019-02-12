# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "hr_org_chart._assets_backend_helpers", "hr_org_chart._assets_primary_variables")
