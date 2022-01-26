# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_mail_server
           SET smtp_authentication = 'gmail'
         WHERE use_google_gmail_service = TRUE
        """
    )
