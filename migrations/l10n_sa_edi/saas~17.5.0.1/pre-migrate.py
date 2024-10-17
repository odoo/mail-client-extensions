import base64

from odoo.exceptions import UserError

from odoo.upgrade import util
from odoo.upgrade.util import json


def migrate(cr, version):
    util.create_column(
        cr, "res_company", "l10n_sa_private_key_id", "int4", fk_table="certificate_key", on_delete_action="SET NULL"
    )
    util.create_column(
        cr,
        "account_journal",
        "l10n_sa_production_csid_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )
    util.create_column(
        cr,
        "account_journal",
        "l10n_sa_compliance_csid_certificate_id",
        "int4",
        fk_table="certificate_certificate",
        on_delete_action="SET NULL",
    )

    cr.execute("SELECT id, l10n_sa_private_key FROM res_company WHERE l10n_sa_private_key IS NOT NULL")

    queries = []
    for company_id, pkey_binary in cr.fetchall():
        # Create a new key and set its reference in the company
        new_key = util.env(cr)["certificate.key"].create(
            {
                "name": f"l10n_sa_edi_{company_id}",
                "content": pkey_binary.tobytes(),
                "company_id": company_id,
            }
        )

        queries.append(
            cr.mogrify(
                "UPDATE res_company SET l10n_sa_private_key_id = %s WHERE id = %s",
                [new_key.id, company_id],
            ).decode()
        )

    util.parallel_execute(cr, queries)

    CERTCERT = util.env(cr)["certificate.certificate"]
    cr.commit()
    cr.execute("""
        SELECT j.id,
               c.id,
               j.l10n_sa_production_csid_json,
               j.l10n_sa_compliance_csid_json,
               c.l10n_sa_private_key_id
          FROM account_journal AS j
          JOIN res_company AS c
            ON j.company_id = c.id
         WHERE j.l10n_sa_production_csid_json IS NOT NULL
           AND j.l10n_sa_compliance_csid_json IS NOT NULL
           AND c.l10n_sa_private_key_id IS NOT NULL
    """)
    queries = []
    for j_id, company_id, l10n_sa_production_csid_json, l10n_sa_compliance_csid_json, private_key_id in cr.fetchall():
        production_csid_json = json.loads(l10n_sa_production_csid_json)
        compliance_csid_json = json.loads(l10n_sa_compliance_csid_json)

        prod_cert = CERTCERT.create(
            {
                "name": f"pcsid_{j_id}_certificate",
                "content": base64.b64decode(production_csid_json["binarySecurityToken"]),
                "company_id": company_id,
            }
        )
        comp_cert = CERTCERT.create(
            {
                "name": f"ccsid_{j_id}_certificate",
                "content": base64.b64decode(compliance_csid_json["binarySecurityToken"]),
                "company_id": company_id,
            }
        )

        queries.append(
            cr.mogrify(
                """
                UPDATE account_journal
                   SET l10n_sa_production_csid_certificate_id = %s,
                       l10n_sa_compliance_csid_certificate_id = %s
                 WHERE account_journal.id = %s;
                """,
                [prod_cert.id, comp_cert.id, j_id],
            ).decode()
        )

        cr.commit()

        # Ensure certificates are created even if the private key changes between journal
        # generations, as the private key is shared among several journals.
        try:
            (prod_cert + comp_cert).write({"private_key_id": private_key_id})
        except UserError:
            cr.rollback()

    util.parallel_execute(cr, queries)

    util.remove_column(cr, "account_journal", "l10n_sa_production_csid_validity")
    util.remove_field(cr, "res.company", "l10n_sa_private_key")
