def migrate(cr, version):
    cr.execute(
        """
        UPDATE website
           SET block_third_party_domains = False
         WHERE cookies_bar = True
           AND NULLIF(google_analytics_key, '') IS NULL
        """
    )
