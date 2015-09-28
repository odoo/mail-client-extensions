# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def is_helpdesk_used(cr):
    if not util.module_installed(cr, 'crm_helpdesk'):
        return False
    # FIXME determine if the module is really used
    cr.execute("""SELECT count(*)
                    FROM crm_helpdesk h
               LEFT JOIN ir_model_data d ON (d.model = 'crm.helpdesk' AND d.res_id = h.id)
                   WHERE coalesce(d.module, '__export__') = '__export__'
               """)
    if cr.fetchone() == (0,):
        return False
    return True

def migrate(cr, version):
    if not is_helpdesk_used(cr):
        util.remove_module(cr, 'crm_helpdesk')
        return

    util.force_install_module(cr, 'project_issue')
    util.force_migration_of_fresh_module(cr, 'project_issue')
