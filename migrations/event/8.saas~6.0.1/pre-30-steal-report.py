# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.module_installed(cr, 'event_sale'):
        return

    xids = {
        'paperformat_euro_lowmargin': 'paperformat_euro_lowmargin',
        'report_registrationbadge': 'report_registration_badge',
        'action_report_registrationbadge': 'action_report_registration_badge',
    }
    for f, t in xids.items():
        util.rename_xmlid(cr, 'event_sale.' + f, 'event.' + t)
