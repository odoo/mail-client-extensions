# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'hr.view_users_form_mail')
    util.remove_view(cr, 'hr.view_human_resources_configuration')
