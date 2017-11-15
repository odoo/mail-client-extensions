# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'quality_point', 'test_type_id', 'int4')
    cr.execute("ALTER TABLE quality_point RENAME COLUMN test_type TO _test_type")
