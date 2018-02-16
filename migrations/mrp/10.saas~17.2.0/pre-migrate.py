# -*- coding: utf-8 -*-
from odoo.release import version_info
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if version_info[:2] == (10, 'saas~17'):
        raise util.MigrationError('Sorry. Migration of module `mrp` need direct migration to version 11.0')
