# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.env(cr)['res.config.settings'].create({
        'group_subtask_project': True,
    }).execute()
