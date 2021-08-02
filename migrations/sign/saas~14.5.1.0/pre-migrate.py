# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.sign_template_mail_follower")

    util.create_column(cr, "sign_request", "subject", "varchar")
    util.create_column(cr, "sign_request", "message", "text")
    util.create_column(cr, "sign_request", "message_cc", "text")
    util.create_column(cr, "sign_send_request", "message_cc", "text")
    util.create_column(cr, "sign_item_role", "color", "integer")

    # random color from [1, 2, 4, 5, 6, 7, 8]
    cr.execute(
        """
        UPDATE sign_item_role
        SET color = CASE name
                        WHEN 'Customer' THEN 3
                        WHEN 'Company' THEN 9
                        WHEN 'Employee' THEN 10
                        WHEN 'HR Responsible' THEN 11
                        ELSE (array[1,2,4,5,6,7,8])[floor(random() * 7 + 1)]
                    END
        """
    )

    cr.execute(
        """
        UPDATE sign_request
           SET subject = 'Signature Request - ' || ia.name
          FROM sign_template st
          JOIN ir_attachment ia on st.attachment_id = ia.id
         WHERE sign_request.template_id = st.id
        """
    )

    util.create_column(cr, "res_company", "sign_terms_type", "varchar", default="plain")

    terms = """<h1 style="text-align: center;">Terms &amp; Conditions</h1><p>Your conditions...</p>"""
    util.create_column(cr, "res_company", "sign_terms", "text", default=terms)
    util.create_column(cr, "res_company", "sign_terms_html", "text", default=terms)
