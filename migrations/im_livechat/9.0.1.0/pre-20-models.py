# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'mail_channel', 'livechat_channel_id', 'int4')
    util.create_column(cr, 'mail_channel', 'anonymous_name', 'varchar')
    cr.execute("""
        UPDATE mail_channel c
           SET livechat_channel_id=s.channel_id,
               anonymous_name=s.anonymous_name,
               channel_type='livechat'
          FROM im_chat_session s
         WHERE s.uuid = c.uuid
           AND s.channel_id IS NOT NULL
    """)

    util.delete_model(cr, 'im_livechat.report')
