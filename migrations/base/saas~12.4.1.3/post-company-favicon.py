# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    Company = util.env(cr)["res.company"]
    for company in Company.search([]):
        company.favicon = Company._get_default_favicon()
