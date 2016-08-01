# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = util.splitlines("""
        action_contacts
        action_contacts_view_kanban
        action_contacts_view_tree
        action_contacts_view_form
        menu_contacts
    """)
    for x in xids:
        util.rename_xmlid(cr, 'mail.' + x, 'contacts.' + x)
    util.force_noupdate(cr, 'contacts.menu_contacts', False)
