# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    if util.parse_version(version) < util.parse_version('10.saas~17'):
        saas17 = util.import_script('website_subscription/10.saas~17.1.0/pre-migrate.py')
        saas17.migrate(cr, version, module='sale_subscription')

    if not util.column_exists(cr, 'sale_subscription', 'uuid'):
        # field moved from website_subscription. Boostrap only if module wasn't installed.
        util.create_column(cr, 'sale_subscription', 'uuid', 'varchar')
        cr.execute("""
            UPDATE sale_subscription
               SET "uuid" = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
             WHERE "uuid" IS NULL
        """)
