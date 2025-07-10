def migrate(cr, version):
    cr.execute("""
        WITH updated_xml_ids AS (
            UPDATE ir_model_data imd
               SET name = concat(imd.name, '_old'),
                   noupdate = true
              FROM res_company rc
              JOIN res_country c ON c.id = rc.account_fiscal_country_id
             WHERE c.code = 'IN'
               AND imd.model = 'documents.document'
               AND imd.module = 'l10n_in_reports_gstr_spreadsheet'
               AND imd.name = concat(rc.id, '_gstr_folder')
         RETURNING imd.res_id
        )

        UPDATE documents_document doc
           SET name = 'GSTR old'
          FROM updated_xml_ids xid
         WHERE doc.id = xid.res_id
    """)
