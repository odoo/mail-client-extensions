# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sign_request_item", "sms_number", "varchar")
    util.create_column(cr, "sign_request_item", "signer_email", "varchar")
    util.create_column(cr, "sign_request_item", "access_via_link", "boolean")
    util.create_column(cr, "sign_template", "redirect_url_text", "varchar")

    cr.execute(
        """
        UPDATE sign_request_item s
           SET sms_number=p.mobile,
               signer_email=p.email
          FROM res_partner p
         WHERE p.id=s.partner_id
        """
    )
    cr.execute("UPDATE sign_template SET redirect_url_text='Open Link'")
    cr.execute("DELETE FROM sign_send_request_signer")

    util.remove_field(cr, "sign.template", "extension")
    util.remove_field(cr, "sign.send.request", "extension")
    util.remove_model(cr, "sign.item.value")
