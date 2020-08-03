# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_users", "last_seen_phone_call", "int4")
    util.remove_model(cr, "voip.phonecall.transfer.wizard")

    cr.execute(
        """
        WITH call AS (
            SELECT DISTINCT ON (user_id)
                   user_id,
                   id
              FROM voip_phonecall
             WHERE call_date IS NOT NULL
               AND in_queue IS TRUE
          ORDER BY user_id, call_date DESC
        )
        UPDATE res_users u
           SET last_seen_phone_call = call.id
          FROM call
         WHERE u.id = call.user_id
    """
    )
