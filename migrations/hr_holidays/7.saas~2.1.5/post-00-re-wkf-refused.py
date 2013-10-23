# -*- coding: utf-8 -*-
def migrate(cr, version):
    """In saas-2, hr_holiday "refused" workflow activity is not flow_stop anymore. Reactivate instances"""

    cr.execute("""UPDATE wkf_instance
                     SET state=%s
                   WHERE res_type=%s
                     AND res_id IN (SELECT id
                                      FROM hr_holidays
                                     WHERE state=%s)
               """, ('active', 'hr.holidays', 'refuse'))
