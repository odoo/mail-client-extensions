# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # deleted modules
    util.remove_module(cr, 'base_status')
    util.remove_module(cr, 'base_partner_merge')    # only for custom/private

    # new dependance
    util.new_module_dep(cr, 'l10n_be', 'l10n_multilang')
    util.new_module_dep(cr, 'crm', 'web_kanban_sparkline')
    util.new_module_dep(cr, 'crm_partner_assign', 'portal')
    util.new_module_dep(cr, 'sale_crm', 'web_kanban_gauge')
    util.new_module_dep(cr, 'google_base_account', 'base_setup')

    # google_docs module is special case
    # it's not a module rename but a replacement with similar functionality
    cr.execute("""SELECT state
                    FROM ir_module_module
                   WHERE name=%s
               """, ('google_docs',))
    doc_state, = cr.fetchone() or ['uninstalled']
    doc_state = {
        'to remove': 'uninstalled',
        'installed': 'to install',
        'to upgrade': 'to install',
    }.get(doc_state, doc_state)
    util.remove_module(cr, 'google_docs')
    cr.execute('INSERT INTO ir_module_module(name, state) VALUES(%s,%s)', ('google_drive', doc_state))
