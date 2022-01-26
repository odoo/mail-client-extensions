# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE fetchmail_server
           SET server_type = 'gmail'
         WHERE use_google_gmail_service = TRUE
        """
    )
