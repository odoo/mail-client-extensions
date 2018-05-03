# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.env(cr).ref('base.group_user').write({
        'implied_ids': [(4, util.ref('analytic.group_analytic_tags'))],
    })
