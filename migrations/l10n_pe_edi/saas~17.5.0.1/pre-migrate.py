from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_pe_edi_certificate_id", drop_column=False)
    # Removing the field from __renamed_fields to bypass the respawn check (a new field with the same name is created)
    util.ENVIRON["__renamed_fields"]["res.company"].pop("l10n_pe_edi_certificate_id")
    cr.execute("ALTER TABLE res_company RENAME COLUMN l10n_pe_edi_certificate_id TO _upg_l10n_pe_edi_certificate_id")
    util.create_column(
        cr,
        "res_company",
        "l10n_pe_edi_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    # Create a temporary column to store and retrieve the old certificate ID from the new certificate
    util.create_column(cr, "certificate_certificate", "_upg_old_id", "int4")

    cr.execute("""
        WITH old_certificates AS (
            SELECT crt.id AS _upg_old_id,
                   att.name AS name,
                   crt.password AS pkcs12_password,
                   crt.company_id
              FROM l10n_pe_edi_certificate AS crt
              JOIN ir_attachment AS att
                ON att.res_id = crt.id
             WHERE att.res_model = 'l10n_pe_edi.certificate'
               AND att.res_field = 'content'
        ), new_certificates AS (
            INSERT INTO certificate_certificate (
                name, pkcs12_password, company_id, active, _upg_old_id
            )
            SELECT name, pkcs12_password, company_id, True, _upg_old_id
              FROM old_certificates
            RETURNING id, _upg_old_id, company_id
        ), updated_att AS (
            UPDATE ir_attachment ia
               SET res_id = nc.id,
                   res_model = 'certificate.certificate'
              FROM new_certificates nc
             WHERE ia.res_id = nc._upg_old_id
               AND ia.res_model = 'l10n_pe_edi.certificate'
               AND ia.res_field = 'content'
        )
        UPDATE res_company rc
           SET l10n_pe_edi_certificate_id = nc.id
          FROM new_certificates nc
         WHERE rc.id = nc.company_id
           AND rc._upg_l10n_pe_edi_certificate_id = nc._upg_old_id;
        """)

    util.remove_column(cr, "certificate_certificate", "_upg_old_id")
    util.remove_model(cr, "l10n_pe_edi.certificate")
    util.remove_column(cr, "res_company", "_upg_l10n_pe_edi_certificate_id")
