# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Due to a bug in the workflow engine, which try to trigger signals to non-loaded modules,
    # `account` module can't be migrated.
    # Droping workflow here instead of own module have no incidence and allow us to not compute
    # complex computed field in sql.

    # There is a relevant xkcd for everything: https://xkcd.com/1172/
    util.drop_workflow(cr, 'sale.order')
    util.drop_workflow(cr, 'purchase.order')
