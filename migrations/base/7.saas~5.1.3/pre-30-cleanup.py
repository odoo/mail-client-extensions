# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # this views is auto-generated when updating res.groups
    util.remove_record(cr, 'base.user_groups_view')
