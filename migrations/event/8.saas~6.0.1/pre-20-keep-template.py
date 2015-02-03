# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    tid = util.ref(cr, 'event.confirmation_registration')
    for table, fk, _, act in util.get_fk(cr, 'mail_template'):
        if act != 'c':      # ignore delete cascade
            cr.execute("SELECT 1 FROM {table} WHERE {fk}=%s".format(table=table, fk=fk), [tid])
            if cr.rowcount:
                # used mail.template -> force noupdate
                util.force_noupdate(cr, 'event.confirmation_registration')
                break
