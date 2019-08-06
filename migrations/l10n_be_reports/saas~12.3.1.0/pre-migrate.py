# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_model(cr, 'l10n_be_reports.periodic.vat.xml.export')
