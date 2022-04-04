# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # The mail sent for new coupons after the order was validated used to be implicit
    # it is now configurable and needs to be set on old programs
    env = util.env(cr)
    gift_card_template = env.ref("loyalty.mail_template_gift_card")
    future_promotion_template = env.ref("loyalty.mail_template_loyalty_card")
    cr.execute(
        """
        INSERT INTO loyalty_mail (
            active, program_id, trigger, points,
            mail_template_id
        )
        SELECT True, p.id, 'create', 0,
            CASE WHEN p.program_type = 'gift_card' THEN %s ELSE %s END
          FROM loyalty_program p
     LEFT JOIN loyalty_mail m
            ON m.program_id = p.id
         WHERE m.id IS NULL -- Ignore programs with loyalty_mails
           AND (p.program_type = 'gift_card'
            OR (p.program_type IN ('coupons', 'promotion')
           AND p.applies_on = 'future'))
        """,
        (gift_card_template.id, future_promotion_template.id),
    )
