# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        WITH attachments AS (
            DELETE FROM ir_attachment
                  WHERE type='binary'
                    AND url ~ '^/'
                    AND name ~ '^(/|https?://)'
                    AND name != url
                    AND store_fname IS NULL
                    AND db_datas IS NULL
            RETURNING id, name, url
        ),
        _rm_imd AS (
            DELETE FROM ir_model_data
                  WHERE model = 'ir.attachment'
                    AND res_id IN (SELECT id FROM attachments)
        )
        INSERT INTO website_redirect(url_from, url_to, type, active, sequence)
            SELECT url, name, '301', true, 1
              FROM attachments
    """)
