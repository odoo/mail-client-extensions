# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'mail_mail_statistics', 'state', 'varchar')
    util.create_column(cr, 'mail_mail_statistics', 'state_update', 'timestamp without time zone')
    cr.execute("""UPDATE mail_mail_statistics
                     SET state_update=write_date,
                         state=CASE WHEN bounced IS NOT NULL THEN 'bounced'
                                    WHEN replied IS NOT NULL THEN 'replied'
                                    WHEN opened IS NOT NULL THEN 'opened'
                                    WHEN sent IS NOT NULL THEN 'sent'
                                    WHEN "exception" IS NOT NULL THEN 'exception'
                                    ELSE NULL
                                END
               """)

    cr.execute("UPDATE mail_mass_mailing SET state='draft' WHERE state='test'")
