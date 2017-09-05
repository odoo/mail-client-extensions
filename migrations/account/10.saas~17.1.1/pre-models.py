# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        message_channel_ids
        message_follower_ids
        message_ids
        message_is_follower
        message_last_post
        message_needaction
        message_needaction_counter
        message_partner_ids
        message_unread
        message_unread_counter
    """)
    for field in fields:
        util.remove_field(cr, 'account.move', field)

    cr.execute("DELETE FROM mail_message WHERE model='account.move'")
    cr.execute("DELETE FROM mail_followers WHERE res_model='account.move'")

    util.create_column(cr, 'account_move_line', 'tax_base_amount', 'numeric')
    cr.execute("""
        WITH line_taxes(id, taxes) AS (
            SELECT account_move_line_id, array_agg(account_tax_id)
              FROM account_move_line_account_tax_rel
          GROUP BY account_move_line_id
        ),
        move_lines(id, tba) AS(
            SELECT l.id, abs(sum(ol.balance))
              FROM account_move_line l
              JOIN account_move_line ol ON (ol.move_id = l.move_id)
              JOIN line_taxes lt ON (ol.id = lt.id)
             WHERE l.tax_line_id = ANY(lt.taxes)
          GROUP BY l.id
        )

        UPDATE account_move_line l
           SET tax_base_amount = m.tba
          FROM move_lines m
         WHERE m.id = l.id
    """)
    cr.execute("UPDATE account_move_line SET tax_base_amount = 0 WHERE tax_base_amount IS NULL")
