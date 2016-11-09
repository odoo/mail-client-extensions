# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xid = 'account.email_template_edi_invoice'
    old_id = util.ref(cr, xid + '_old')
    if old_id:
        new_id = util.ref(cr, xid)
        util.replace_record_references(cr, ('mail.template', old_id), ('mail.template', new_id), False)
        util.remove_record(cr, xid + '_old')
