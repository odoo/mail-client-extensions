# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'website_crm.contactus_form_company_name')
    util.force_noupdate(cr, 'website_crm.contactus_form', False)
    util.force_noupdate(cr, 'website_crm.contactus_thanks', False)
