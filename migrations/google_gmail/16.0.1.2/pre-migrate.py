# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_mail_server
           SET smtp_pass = NULL,
               smtp_encryption = 'starttls',
               from_filter = smtp_user
         WHERE smtp_authentication = 'gmail'
        """
    )
