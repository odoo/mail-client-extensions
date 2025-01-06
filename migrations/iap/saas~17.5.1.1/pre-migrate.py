from odoo.upgrade import util


def migrate(cr, version):
    module_iap_invoice_map = {
        "iap_extract": "invoice_ocr",
        "sign_itsme": "itsme_proxy",
        "l10n_in_edi": "l10n_in_edi",
        "l10n_br_avatax": "l10n_br_avatax_proxy",
        "l10n_pe_edi": "l10n_pe_edi",
        "partner_autocomplete": "partner_autocomplete",
        "sms": "sms",
        "snailmail": "snailmail",
    }

    iap_account_without_module = {
        iap_account for module, iap_account in module_iap_invoice_map.items() if not util.module_installed(cr, module)
    }

    if iap_account_without_module:
        cr.execute("SELECT id FROM iap_account WHERE service_name IN %s", [tuple(iap_account_without_module)])
        util.remove_records(cr, "iap.account", [aid for (aid,) in cr.fetchall()])

    cr.execute("""
        CREATE TABLE iap_service (
            id SERIAL NOT NULL PRIMARY KEY,
            name varchar,
            technical_name varchar,
            write_uid integer,
            write_date timestamp without time zone,
            description jsonb,
            unit_name jsonb,
            integer_balance boolean
        )
    """)

    cr.execute("""
        INSERT INTO iap_service (technical_name, integer_balance)
             SELECT service_name, false
               FROM iap_account
              WHERE service_name IS NOT NULL
              GROUP BY service_name
    """)

    util.remove_model(cr, "iap.account.info")

    util.remove_field(cr, "iap.account", "show_token")
    util.remove_field(cr, "iap.account", "warning_email")
    util.remove_field(cr, "iap.account", "warn_me")
    util.remove_field(cr, "iap.account", "account_info_id")
    util.remove_field(cr, "iap.account", "account_info_ids")

    util.create_column(cr, "iap_account", "service_id", "int4")

    cr.execute("""
        UPDATE iap_account
           SET service_id = iap_service.id
          FROM iap_service
         WHERE iap_account.service_name = iap_service.technical_name""")

    util.remove_column(cr, "iap_account", "service_name")
