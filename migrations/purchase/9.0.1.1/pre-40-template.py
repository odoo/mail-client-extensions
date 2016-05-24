# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE mail_template
           SET email_from=replace(email_from, 'object.validator', 'object.create_uid'),
               body_html=replace(body_html, 'object.validator', 'object.create_uid')
         WHERE id IN %s
    """, [(util.ref(cr, 'purchase.email_template_edi_purchase'),
           util.ref(cr, 'purchase.email_template_edi_purchase_done'))])
