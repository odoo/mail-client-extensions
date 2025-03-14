from odoo.upgrade import util


def migrate(cr, version):
    query = """
                WITH invalid_thumbnail_status AS (
                    SELECT d.id
                      FROM documents_document d
                      JOIN ir_attachment a
                        ON a.res_model = 'documents.document'
                       AND a.res_id = d.id
                       AND a.res_field = 'thumbnail'
                     WHERE d.thumbnail_status IS NULL
                       AND {parallel_filter}
                )
                UPDATE documents_document d
                   SET thumbnail_status = 'present'
                  FROM invalid_thumbnail_status invalid
                 WHERE d.id = invalid.id
            """
    util.explode_execute(cr, query, table="documents_document", alias="d")
