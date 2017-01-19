# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def get_template(cr, xid):
    tid = util.ref(cr, xid)
    cr.execute("""SELECT 1
                    FROM mail_template
                   WHERE id=%s
                     AND coalesce(write_date, create_date) - create_date > interval '1 hour'
               """, [tid])
    modified = cr.rowcount != 0
    return tid, modified

def migrate(cr, version):
    # update DP name
    dp = util.ref(cr, 'account.decimal_payment')
    if dp:
        cr.execute("UPDATE decimal_precision SET name='Payment Terms' WHERE id=%s", [dp])

    # let ORM update template
    xid = 'account.email_template_edi_invoice'
    tid, modified = get_template(cr, xid)
    if not modified:
        # As the the new template is defined in a noupdate section,
        # only the presence of the xid is check, not it noupdate value.
        # rename xmlid to force creation of new one (references will be replaced in post-script)
        util.rename_xmlid(cr, xid, xid + '_old')

    # update other views
    util.force_noupdate(cr, 'account.report_invoice_document', False)
