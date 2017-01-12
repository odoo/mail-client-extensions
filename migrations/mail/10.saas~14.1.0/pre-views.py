# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'mail.view_emails_partner_info_form',
                      'mail.res_partner_view_form_inherit_mail')
    util.rename_xmlid(cr, 'mail.res_partner_opt_out_search',
                      'mail.res_partner_view_search_inherit_mail')
