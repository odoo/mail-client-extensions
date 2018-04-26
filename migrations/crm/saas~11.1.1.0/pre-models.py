# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'crm_lead', 'planned_revenue')
    cr.execute("ALTER TABLE crm_lead ALTER COLUMN planned_revenue TYPE numeric")
