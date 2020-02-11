# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE marketing_activity AS main_activity
           SET trigger_type = CASE
                                WHEN main_activity.trigger_type = 'mail_click' THEN 'sms_click'
                                WHEN main_activity.trigger_type = 'mail_not_click' THEN 'sms_not_click'
                                ELSE 'sms_bounce'
                              END
          FROM marketing_activity AS parent_activity
         WHERE parent_activity.id = main_activity.parent_id
           AND main_activity.trigger_type = ANY(ARRAY['mail_not_click', 'mail_click', 'mail_bounce'])
           AND parent_activity.activity_type = 'sms'
      """)
