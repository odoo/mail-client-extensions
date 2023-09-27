# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE website_page
           SET url = '/no-url-migration-odoo-16.5.1', is_published = FALSE
         WHERE url IS NULL
        """
    )
