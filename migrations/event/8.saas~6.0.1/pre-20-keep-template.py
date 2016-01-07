# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def get_template(cr):
    tid = util.ref(cr, 'event.confirmation_registration')
    cr.execute("""SELECT 1
                    FROM mail_template
                   WHERE id=%s
                     AND coalesce(write_date, create_date) - create_date > interval '1 hour'
               """, [tid])
    modified = cr.rowcount != 0
    return tid, modified

def migrate(cr, version):
    tid, modified = get_template(cr)
    if not modified:
        # As the the new template is defined in a noupdate section,
        # only the presence of the xid is check, not it noupdate value.
        # So, let the system create a new template,
        # we will reassign record references in related post script.
        util.force_noupdate(cr, 'event.confirmation_registration', False)
        return

    for table, fk, _, act in util.get_fk(cr, 'mail_template'):
        if act != 'c':      # ignore delete cascade
            cr.execute("SELECT 1 FROM {table} WHERE {fk}=%s".format(table=table, fk=fk), [tid])
            if cr.rowcount:
                # used mail.template -> force noupdate
                util.force_noupdate(cr, 'event.confirmation_registration')
                # but make it compatible
                cr.execute("""UPDATE mail_template
                                 SET email_from=replace(email_from, '{f}', '{t}'),
                                     email_to=replace(email_to, '{f}', '{t}'),
                                     reply_to=replace(reply_to, '{f}', '{t}'),
                                     subject=replace(subject, '{f}', '{t}'),
                                     lang=replace(lang, '{f}', '{t}'),
                                     body_html=replace(body_html, '{f}', '{t}')
                               WHERE id=%s
                           """.format(f="object.user_id", t="object.event_id.organizer_id"),
                           [tid])
                break
