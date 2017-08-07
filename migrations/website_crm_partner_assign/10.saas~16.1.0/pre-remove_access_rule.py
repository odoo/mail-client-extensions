# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'website_crm_partner_assign.mail_message_subtype_portal_access')
