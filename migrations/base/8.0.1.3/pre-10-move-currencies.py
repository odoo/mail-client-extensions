#-*- encoding: utf8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'l10n_gt.rateGTQ', 'base.rateGTQ')
    util.rename_xmlid(cr, 'l10n_gt.GTQ', 'base.GTQ')

