# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.env(cr)['res.config.settings'].create({
        'group_analytic_tags': True,
    }).execute()
