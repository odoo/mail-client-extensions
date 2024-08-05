def migrate(cr, version):
    cr.execute("""
        UPDATE iap_account
           SET name = iap_service.name
          FROM iap_service
         WHERE iap_account.service_id = iap_service.id
           AND iap_account.name IS NULL
    """)
