from odoo.upgrade import util


def migrate(cr, version):
    # Column removed at the end, used to link the attachment
    util.create_column(cr, "l10n_es_edi_tbai_certificate", "_upg_source_id", "int4")

    cr.execute("""
        INSERT INTO l10n_es_edi_tbai_certificate(
                        password,
                        date_start,
                        date_end,
                        company_id,
                        _upg_source_id
                    )
             SELECT sc.password,
                    sc.date_start,
                    sc.date_end,
                    sc.company_id,
                    sc.id
               FROM l10n_es_edi_sii_certificate sc
               JOIN res_company rc
                 ON sc.company_id = rc.id
              WHERE rc.l10n_es_tbai_tax_agency IS NOT NULL
    """)

    cr.execute("""
        UPDATE ir_attachment ia
           SET res_model = 'l10n_es_edi_tbai.certificate',
               res_id = tc.id
          FROM l10n_es_edi_tbai_certificate tc
         WHERE ia.res_model = 'l10n_es_edi_sii.certificate'
           AND ia.res_id = tc._upg_source_id
    """)

    cr.execute("SELECT _upg_source_id FROM l10n_es_edi_tbai_certificate")
    util.remove_records(cr, "l10n_es_edi_sii.certificate", [sii_cert_id for (sii_cert_id,) in cr.fetchall()])

    cr.execute("UPDATE res_company SET l10n_es_tbai_test_env = l10n_es_sii_test_env")

    util.remove_column(cr, "l10n_es_edi_tbai_certificate", "_upg_source_id")
