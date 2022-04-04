# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_mail_server
           SET smtp_authentication = 'gmail'
         WHERE use_google_gmail_service = TRUE
        """
    )

    if util.column_exists(cr, "fetchmail_server", "use_google_gmail_service"):
        cr.execute(
            """
            UPDATE fetchmail_server
               SET server_type = 'gmail'
             WHERE use_google_gmail_service = TRUE
            """
        )
