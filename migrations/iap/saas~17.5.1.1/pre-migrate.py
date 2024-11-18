from odoo.upgrade import util


def migrate(cr, version):
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
