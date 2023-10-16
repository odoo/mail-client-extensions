# -*- coding:utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_mail_server
           SET smtp_authentication = 'outlook',
               from_filter = smtp_user
         WHERE use_microsoft_outlook_service = TRUE
        """
    )
    if util.column_exists(cr, "fetchmail_outlook", "use_microsoft_outlook_service"):
        cr.execute(
            """
            UPDATE fetchmail_server
               SET server_type = 'outlook'
             WHERE use_microsoft_outlook_service = TRUE
            """
        )
