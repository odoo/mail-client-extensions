# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'base_action_rule', 'kind', 'varchar')

    cr.execute("""UPDATE base_action_rule
                     SET kind = CASE
                                  WHEN trg_date_id IS NULL AND filter_pre_id IS NULL     THEN 'on_create_or_write'
                                  WHEN trg_date_id IS NULL AND filter_pre_id IS NOT NULL THEN 'on_write'
                                  WHEN trg_date_id IS NOT NULL                           THEN 'on_time'
                                  ELSE 'on_write'
                                END
                   WHERE kind IS NULL
               """)
