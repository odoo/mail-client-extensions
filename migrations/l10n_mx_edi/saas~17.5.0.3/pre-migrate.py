from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "l10n_mx_edi_certificate_id", drop_column=False)
    # Removing the field from __renamed_fields to bypass the respawn check (a new field with the same name is created)
    util.ENVIRON["__renamed_fields"]["account.move"].pop("l10n_mx_edi_certificate_id")
    cr.execute("ALTER TABLE account_move RENAME COLUMN l10n_mx_edi_certificate_id TO _upg_l10n_mx_edi_certificate_id")
    util.create_column(
        cr,
        "account_move",
        "l10n_mx_edi_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    CERTKEY = util.env(cr)["certificate.key"]
    CERTCERT = util.env(cr)["certificate.certificate"]

    cr.execute("SELECT id, content, key, password, company_id FROM l10n_mx_edi_certificate")
    queries = []

    for old_id, content, key, password, company_id in cr.fetchall():
        # Create certificates and keys using ORM to ensure all business logic and constraints are applied
        # This guarantees data integrity and triggers necessary compute methods
        new_key = CERTKEY.create(
            {
                "name": f"l10n_mx_key_{old_id}_{company_id}.key",
                "content": key,
                "password": password,
                "company_id": company_id,
            }
        )
        new_crt = CERTCERT.create(
            {
                "name": f"l10n_mx_certificate_{old_id}_{company_id}",
                "content": content,
                "private_key_id": new_key.id,
                "company_id": company_id,
            }
        )

        # Use raw SQL for bulk updates to improve performance
        # The ORM can be slower for large-scale updates due to its overhead
        queries.append(
            cr.mogrify(
                """
                UPDATE account_move
                   SET l10n_mx_edi_certificate_id = %s
                 WHERE company_id = %s
                   AND _upg_l10n_mx_edi_certificate_id = %s
                """,
                [new_crt.id, company_id, old_id],
            ).decode()
        )

    util.parallel_execute(cr, queries)

    util.remove_column(cr, "account_move", "_upg_l10n_mx_edi_certificate_id")
    util.remove_model(cr, "l10n_mx_edi.certificate")
