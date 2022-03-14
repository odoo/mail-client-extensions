# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE mail_template
           SET subject = regexp_replace(subject, '\yobject.number\y', 'object.name', 'g'),
               body_html = regexp_replace(body_html, '\yobject.number\y', 'object.name', 'g'),
               report_name = regexp_replace(report_name, '\yobject.number\y', 'object.name', 'g')
         WHERE id = %s
            AND (  subject like '%%object.number%%'
                OR body_html like '%%object.number%%'
                OR report_name like '%%object.number%%'
                )
        """,
        [util.ref(cr, "account.email_template_edi_invoice")],
    )
