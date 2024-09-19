from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr,
        "account_edi_proxy_client_user",
        "private_key_id",
        "int4",
        fk_table="certificate_key",
        on_delete_action="RESTRICT",
    )

    CERTKEY = util.env(cr)["certificate.key"]

    cr.execute(
        """
        SELECT id, private_key, company_id,
               CONCAT(id_client, '_', edi_identification, '.key') as filename
          FROM account_edi_proxy_client_user
         WHERE private_key IS NOT NULL
        """
    )
    queries = []

    for id_, pk, cid, fn in cr.fetchall():
        data = {
            "name": fn,
            "content": pk.tobytes(),
            "company_id": cid,
        }
        key_id = CERTKEY.create(data).id
        queries.append(
            cr.mogrify(
                "UPDATE account_edi_proxy_client_user SET private_key_id = %s WHERE id = %s", [key_id, id_]
            ).decode()
        )

    util.parallel_execute(cr, queries)

    util.remove_field(cr, "account_edi_proxy_client.user", "private_key")
    util.remove_field(cr, "account_edi_proxy_client.user", "private_key_filename")
