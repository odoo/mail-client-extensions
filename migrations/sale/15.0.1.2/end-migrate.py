# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    replaces = [
        (r"\ypayment_token_id\y", "token_id"),
        (r"\yobject.website_id\y", "hasattr(object, 'website_id') and object.website_id"),
        (r"\yobject.carrier_id\y", "hasattr(object, 'carrier_id') and object.carrier_id"),
        (r"\ynot line.is_delivery\y", "(not hasattr(line, 'is_delivery') or not line.is_delivery)"),
        (
            r"""<tr t-attf-style="\{\{ ?loop.cycle\('background-color: ?#f2f2f2', ?'background-color: ?#ffffff'\) ?\}\}">""",
            """<t t-set="loop_cycle_number" t-value="0" />
               <tr t-att-style="'background-color: #f2f2f2' if loop_cycle_number % 2 == 0 \
else 'background-color: #ffffff'">
                    <t t-set="loop_cycle_number" t-value="loop_cycle_number + 1" />""",
        ),
    ]

    template_id = util.ref(cr, "sale.mail_template_sale_confirmation")
    for old, new in replaces:
        cr.execute(
            """
            UPDATE mail_template
               SET body_html = regexp_replace(body_html, %s, %s, 'g')
             WHERE id = %s
            """,
            [old, new, template_id],
        )

        cr.execute(
            """
            UPDATE ir_translation
               SET value = regexp_replace(value, %s, %s, 'g')
             WHERE name IN ('mail.template,body_html', 'mail.template,subject', 'mail.template,report_name')
               AND res_id = %s
            """,
            [old, new, template_id],
        )
