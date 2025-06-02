def migrate(cr, version):
    cr.execute("""
        UPDATE l10n_latam_document_type t
           SET active = TRUE
          FROM res_country c
         WHERE c.id = t.country_id
           AND c.code = 'AR'
           AND t.code IN ('91', '94')
    """)
