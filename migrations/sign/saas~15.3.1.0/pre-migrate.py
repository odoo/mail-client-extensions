# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_item", "transaction_id", "int4")
    util.rename_field(cr, "sign.send.request", "follower_ids", "cc_partner_ids")
    util.remove_model(cr, "sign.request.send.copy")
    util.remove_model(cr, "sign.template.share")
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

    # cancel all sign requests(which has one sign request item whose partner_id is NULL) for old shared links
    cr.execute(
        """
            UPDATE sign_request sr
               SET state = 'canceled'
              FROM sign_request_item sri
             WHERE sr.id = sri.sign_request_id
               AND sri.partner_id is NULL
        """
    )
    cr.execute(
        """
            UPDATE sign_request_item sri
               SET state = 'canceled'
             WHERE sri.partner_id is NULL
        """
    )
    # Create the shared sign request to avoid losing the shared links. The access token field is used to update the controller
    cr.execute(
        """
        INSERT INTO sign_request (reference,template_id,state,access_token,refusal_allowed,active)
        SELECT CONCAT(ia.name, ' - Shared'),
               st.id,
               'shared',
               md5(concat(clock_timestamp()::varchar, ';', random()::varchar))::uuid::varchar,
               false,
               true
          FROM sign_template st
          JOIN ir_attachment ia on st.attachment_id = ia.id
         WHERE st.share_link IS NOT NULL
        """
    )
    default_role_id = util.ref(cr, "sign.sign_item_role_default")
    cr.execute(
        """
            INSERT INTO sign_request_item (sign_request_id,role_id,access_token,state)
            SELECT DISTINCT sr.id,COALESCE(si.responsible_id, %s),st.share_link,'sent'
            FROM sign_request sr
            JOIN sign_template st ON st.id=sr.template_id
            JOIN sign_item si ON si.template_id = st.id
            WHERE sr.state = 'shared'
              AND st.share_link IS NOT NULL
        """,
        [default_role_id],
    )
    util.remove_field(cr, "sign.template", "share_link")
