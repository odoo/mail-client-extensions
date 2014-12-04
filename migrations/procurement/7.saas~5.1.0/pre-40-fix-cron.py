# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    cr.execute("""UPDATE ir_cron
                     SET args='(True,)'
                   WHERE id IN (SELECT res_id
                                  FROM ir_model_data
                                 WHERE module='procurement'
                                   AND name='ir_cron_scheduler_action')
               """)

if __name__ == '__main__':
    util.main(migrate)
