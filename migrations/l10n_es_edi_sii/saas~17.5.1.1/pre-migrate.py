from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_certificate_ids"))
    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_tax_agency"))
    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_test_env"))

    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_certificate_ids"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_tax_agency"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_test_env"))

    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_{ec,es_sii}_digital_certificate"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_es_edi{,_sii}_certificate_action"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.menu_l10n_es_edi{,_sii}_root"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.menu_l10n_es_edi{,_sii}_certificates"))

    util.remove_field(cr, "res.company", "l10n_es_edi_certificate_id", drop_column=False)
    util.create_column(
        cr,
        "res_company",
        "l10n_es_edi_sii_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    # Create a temporary column to store and retrieve the old certificate ID from the new certificate
    util.create_column(
        cr,
        "certificate_certificate",
        "_upg_old_id",
        "int4",
    )

    cr.execute("""
        WITH old_certificates AS (
            SELECT cert.id AS _upg_old_id, ia.name, cert.password, cert.company_id
              FROM l10n_es_edi_certificate AS cert
              JOIN ir_attachment ia
                ON ia.res_id = cert.id
             WHERE ia.res_model = 'l10n_es_edi.certificate'
               AND ia.res_field = 'content'
        ), new_certificates AS (
            INSERT INTO certificate_certificate (name, pkcs12_password, company_id, scope, active, _upg_old_id)
                 SELECT name, password, company_id, 'sii', True, _upg_old_id
                   FROM old_certificates
            RETURNING id, _upg_old_id, company_id
        ), updated_att AS (
            UPDATE ir_attachment ia
               SET res_id = nc.id,
                   res_model = 'certificate.certificate'
              FROM new_certificates nc
             WHERE res_id = nc._upg_old_id
               AND res_model = 'l10n_es_edi.certificate'
               AND res_field = 'content'
        )
        UPDATE res_company rc
           SET l10n_es_edi_sii_certificate_id = nc.id
          FROM new_certificates nc
         WHERE l10n_es_edi_certificate_id = nc._upg_old_id
           AND rc.id = nc.company_id;
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_old_id")
    util.remove_column(cr, "res_company", "l10n_es_edi_certificate_id")
    util.remove_model(cr, "l10n_es_edi.certificate")
