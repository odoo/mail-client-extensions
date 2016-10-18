# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        WITH plaid AS (
            UPDATE account_online_journal j
               SET online_identifier = j.plaid_id
              FROM online_institution i
             WHERE i.id = j.institution_id
               AND lower(i.type) = 'plaid'
         RETURNING j.id, j.institution_id, j.token
        )
        INSERT INTO account_online_provider(
                name, provider_type, provider_account_identifier, provider_identifier, company_id
        )
        SELECT i.name, 'plaid', p.token, i.online_id,
               (SELECT company_id
                  FROM account_journal
                 WHERE account_online_journal_id = ANY(p.journal_ids)
                 LIMIT 1)
          FROM (SELECT token,
                       array_agg(id) as journal_ids, array_agg(institution_id) as inst_ids
                  FROM plaid
              GROUP BY token
                ) p
          JOIN online_institution i ON (i.id = ANY(p.inst_ids))
    """)
    cr.execute("""
        UPDATE account_online_journal j
           SET account_online_provider_id = p.id
          FROM account_online_provider p
         WHERE p.provider_type = 'plaid'
           AND j.token = p.provider_account_identifier
    """)

    util.remove_field(cr, 'account.online.journal', 'plaid_id')
    util.remove_field(cr, 'account.online.journal', 'token')

    online_sync = util.import_script('account_online_sync/9.saas~13.2.0/pre-10-models.py')
    online_sync.cleanup(cr)
