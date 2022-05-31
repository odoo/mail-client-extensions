# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE mail_channel c
           SET name = t.value
          FROM ir_translation t,
               res_users u
          JOIN res_partner p ON p.id = u.partner_id
         WHERE t.name = 'mail.channel,name'
           AND t.res_id = c.id
           AND u.id = c.create_uid
           AND t.lang = p.lang
        """
    )
    cr.execute(
        """
        DELETE
          FROM ir_translation
         WHERE name = 'mail.channel,name'
        """
    )

    util.remove_inherit_from_model(cr, "mail.channel", "mail.alias.mixin")
