# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_item", "transaction_id", "int4")
    util.rename_field(cr, "sign.send.request", "follower_ids", "cc_partner_ids")
    util.remove_model(cr, "sign.request.send.copy")
    util.change_field_selection_values(cr, "sign.request.item", "state", {"draft": "canceled"})

    # change all old 'sent' sign request items in 'refused' sign requests to 'canceled'
    cr.execute(
        """
            UPDATE sign_request_item sri
               SET state = 'canceled'
              FROM sign_request sr
             WHERE sr.id = sri.sign_request_id
               AND sr.state = 'refused'
               AND sri.state = 'sent'
        """
    )

    # set all empty role_id to default sign_item_role
    cr.execute(
        """
            UPDATE sign_request_item
               SET role_id = %s
             WHERE role_id IS NULL
        """,
        [util.ref(cr, "sign.sign_item_role_default")],
    )

    # remove rel of completed documents and certificates from ir_attachment_sign_request_rel
    util.create_m2m(cr, "sign_request_completed_document_rel", "sign_request", "ir_attachment")
    cr.execute(
        """
            DELETE FROM ir_attachment_sign_request_rel ia_sr
                  USING (
                        SELECT sign_request_id, ir_attachment_id
                          FROM ir_attachment_sign_request_rel ia_sr
                          JOIN ir_attachment ia ON ia.id = ia_sr.ir_attachment_id
                          JOIN sign_request sr ON sr.id = ia_sr.sign_request_id
                         WHERE ia.name LIKE 'Certificate of completion%'
                            OR ia.name LIKE 'Activity Logs%'
                            OR ia.name LIKE sr.reference || '%'
                        ) AS rows
                  WHERE ia_sr.sign_request_id = rows.sign_request_id
                    AND ia_sr.ir_attachment_id = rows.ir_attachment_id
        """
    )
    # add rel of completed documents and certificates to sign_request_completed_document_rel
    cr.execute(
        """
            INSERT INTO sign_request_completed_document_rel (ir_attachment_id, sign_request_id)
                 SELECT ia.id AS ir_attachment_id, sr.id AS sign_request_id
                   FROM ir_attachment ia
                   JOIN sign_request sr ON ia.res_model = 'sign.request' AND ia.res_field IS NULL AND ia.res_id = sr.id
                  WHERE ia.name LIKE 'Certificate of completion%'
                     OR ia.name LIKE 'Activity Logs%'
                     OR ia.name LIKE sr.reference || '%'
        """
    )
