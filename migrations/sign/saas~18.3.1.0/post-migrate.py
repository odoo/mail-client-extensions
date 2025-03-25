from odoo.upgrade import util


def migrate(cr, version):
    # Migrate existing template data to new document structure
    cr.execute(
        """
        INSERT INTO sign_document (
            create_uid, create_date, write_uid, write_date,
            sequence, attachment_id, template_id, num_pages
        )
        SELECT create_uid, create_date, write_uid, write_date,
               1, attachment_id, id, num_pages
          FROM sign_template
         WHERE attachment_id IS NOT NULL
        """
    )

    util.explode_execute(
        cr,
        """
        UPDATE sign_item si
           SET document_id = sd.id
          FROM sign_document sd
         WHERE si.template_id = sd.template_id
        """,
        table="sign_item",
        alias="si",
    )

    # Move completed documents to new table and update attachment reference
    cr.execute(
        """
        INSERT INTO sign_completed_document(
            create_uid, create_date, write_uid, write_date,
            sign_request_id, document_id
        )
        SELECT req.create_uid, req.create_date, req.write_uid,
                req.write_date, req.id, doc.id
          FROM sign_request AS req
          JOIN sign_document AS doc
            ON req.template_id = doc.template_id
        """
    )

    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment att
           SET res_model = 'sign.document',
               res_id = sd.id
          FROM sign_document AS sd
         WHERE att.res_model = 'sign.template'
           AND att.res_id = sd.template_id
        """,
        table="ir_attachment",
        alias="att",
    )

    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment att
           SET res_model = 'sign.completed.document',
               res_id = completed.id,
               res_field = 'file'
          FROM sign_completed_document AS completed
         WHERE att.res_model = 'sign.request'
           AND att.res_id = completed.sign_request_id
           AND att.name = 'completed_document'
        """,
        table="ir_attachment",
        alias="att",
    )

    util.remove_column(cr, "sign_template", "num_pages")
    util.remove_column(cr, "sign_template", "attachment_id")
    util.remove_column(cr, "sign_item", "template_id")
