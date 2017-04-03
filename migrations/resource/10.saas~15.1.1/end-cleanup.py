# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # done in an `end-` script because used in mrp migration
    util.remove_field(cr, 'resource.resource', 'code')
