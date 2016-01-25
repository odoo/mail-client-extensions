# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'report_intrastat.report_intrastatinvoice', False)
    util.force_noupdate(cr, 'report_intrastat.report_intrastatinvoice_document', False)
