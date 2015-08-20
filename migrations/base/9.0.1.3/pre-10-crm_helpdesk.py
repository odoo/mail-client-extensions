# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'crm_helpdesk'):
        # FIXME determine if the module is really used
        if not util.module_installed(cr, 'project'):
            util.force_install_module(cr, 'project')
            # TODO create minimal tables

        # TODO convert data to issues

    util.remove_module(cr, 'crm_helpdesk')
