# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    """
    Field 'reviewer_id' is added in saas-5, It should not take a default value.
    """
    util.create_column(cr, 'project_task', 'reviewer_id', 'int4')

