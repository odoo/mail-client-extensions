# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_module(cr, 'base_calendar', 'calendar')
    util.rename_module(cr, 'google_base_account', 'google_account')

    util.new_module_dep(cr, 'calendar', 'web_calendar')
    util.new_module_dep(cr, 'base_action_rule', 'resource')
    util.new_module_dep(cr, 'hr_contract', 'base_action_rule')

    util.remove_module(cr, 'web_shortcuts')

    # new module auto_installed
    deps = ('hr_recruitment', 'document')
    cr.execute("""SELECT count(1)
                    FROM ir_module_module
                   WHERE name IN %s
                     AND state IN %s
               """, (deps, ('to install', 'to upgrade')))

    state = 'to install' if cr.fetchone()[0] == len(deps) else 'uninstalled'
    cr.execute("INSERT INTO ir_module_module(name, state) VALUES (%s, %s)",
               ('hr_applicant_document', state))
