# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def is_claims_used(cr):
    if not util.module_installed(cr, 'crm_claim'):
        return False
    cr.execute("""
        SELECT count(*)
          FROM crm_claim c
     LEFT JOIN ir_model_data d ON (d.model = 'crm.claim' AND d.res_id = c.id)
         WHERE coalesce(d.module, '__export__') = '__export__'
    """)
    return bool(cr.fetchone()[0])

def migrate(cr, version):
    if not is_claims_used(cr):
        util.remove_module(cr, 'crm_claim')
        return

    util.force_install_module(cr, 'project_issue')
    util.force_migration_of_fresh_module(cr, 'project_issue')
