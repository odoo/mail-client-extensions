# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        WITH yodlee AS (
            UPDATE account_online_journal j
               SET online_identifier = j.account_id
              FROM online_institution i
             WHERE i.id = j.institution_id
               AND lower(i.type) = 'yodlee'
         RETURNING j.id, j.institution_id, j.site_account_id
        )
        INSERT INTO account_online_provider(
                name, provider_type, provider_account_identifier, provider_identifier, company_id
        )
        SELECT i.name, 'yodlee', y.site_account_id, i.online_id,
               (SELECT company_id
                  FROM account_journal
                 WHERE account_online_journal_id = ANY(y.journal_ids)
                 LIMIT 1)
          FROM (SELECT site_account_id,
                       array_agg(id) as journal_ids, array_agg(institution_id) as inst_ids
                  FROM yodlee
              GROUP BY site_account_id
                ) y
          JOIN online_institution i ON (i.id = ANY(y.inst_ids))
    """)
    cr.execute("""
        UPDATE account_online_journal j
           SET account_online_provider_id = p.id
          FROM account_online_provider p
         WHERE p.provider_type = 'yodlee'
           AND j.site_account_id = p.provider_account_identifier
    """)

    util.remove_field(cr, 'account.online.journal', 'account_id')
    util.remove_field(cr, 'account.online.journal', 'site_account_id')
