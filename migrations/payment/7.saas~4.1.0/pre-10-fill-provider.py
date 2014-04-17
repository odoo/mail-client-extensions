# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'payment_acquirer', 'provider', 'varchar')
    cr.execute("UPDATE payment_acquirer SET provider=name")
