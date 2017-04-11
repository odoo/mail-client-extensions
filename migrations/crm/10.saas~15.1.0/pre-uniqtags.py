# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.uniq_tags(cr, 'crm.lead.tag', 'lower(name)')
