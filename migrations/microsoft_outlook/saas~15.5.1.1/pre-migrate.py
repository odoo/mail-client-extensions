# -*- coding:utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_mail_server
           SET smtp_authentication = 'outlook',
               from_filter = smtp_user
         WHERE use_microsoft_outlook_service = TRUE
        """
    )

    cr.execute(
        """
        UPDATE fetchmail_server
           SET server_type = 'outlook'
         WHERE use_microsoft_outlook_service = TRUE
        """
    )
