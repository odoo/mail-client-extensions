# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
    WITH to_update AS (
        SELECT d.id
          FROM documents_document AS d
          JOIN ir_attachment AS f
            ON f.id = d.attachment_id
     LEFT JOIN ir_attachment AS thumbnail
            ON thumbnail.res_model = 'documents.document'
           AND thumbnail.res_field = 'thumbnail'
           AND thumbnail.res_id = d.id
         WHERE f.mimetype LIKE 'application/pdf%'
           AND thumbnail.id IS NULL
           AND d.thumbnail_status IS NULL
           AND {parallel_filter}
    )
     UPDATE documents_document
        SET thumbnail_status = 'client_generated'
       FROM to_update
      WHERE documents_document.id = to_update.id;
    """
    util.explode_execute(cr, query, table="documents_document", alias="d")
