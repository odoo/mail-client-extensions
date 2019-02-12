# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("im_livechat.im_livechat_channel_{demo,data}"))

    util.create_column(cr, "mail_channel", "livechat_operator_id", "int4")
    util.create_column(cr, "mail_channel", "country_id", "int4")
    cr.execute("""
      WITH _op AS (
        SELECT channel_id, (array_agg(partner_id ORDER BY id))[1] as partner_id
          FROM mail_channel_partner
      GROUP BY channel_id
      )
        UPDATE mail_channel c
           SET livechat_operator_id = _op.partner_id
          FROM _op
         WHERE _op.channel_id = c.id
           AND c.channel_type = 'livechat'
    """)

    util.create_column(cr, "res_users", "livechat_username", "varchar")
