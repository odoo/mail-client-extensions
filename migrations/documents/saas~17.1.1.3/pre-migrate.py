from odoo.upgrade import util


def migrate(cr, version):
    query = """
    WITH to_update AS (
        SELECT d.id,
               CASE
                   WHEN f.mimetype LIKE 'application/pdf%' AND thumbnail.id IS NULL THEN 'client_generated'
                   WHEN f.mimetype LIKE 'image/%'          AND thumbnail.id IS NOT NULL THEN 'present'
                   ELSE NULL
                END AS new_thumbnail_status
          FROM documents_document AS d
          JOIN ir_attachment AS f
            ON f.id = d.attachment_id
     LEFT JOIN ir_attachment AS thumbnail
            ON thumbnail.res_model = 'documents.document'
           AND thumbnail.res_field = 'thumbnail'
           AND thumbnail.res_id = d.id
         WHERE (
                   (f.mimetype LIKE 'application/pdf%' AND thumbnail.id IS NULL)
                OR (f.mimetype LIKE 'image/%'          AND thumbnail.id IS NOT NULL)
               )
           AND d.thumbnail_status IS NULL
           AND {parallel_filter}
    )
     UPDATE documents_document
        SET thumbnail_status = to_update.new_thumbnail_status
       FROM to_update
      WHERE documents_document.id = to_update.id;
    """
    util.explode_execute(cr, query, table="documents_document", alias="d")
