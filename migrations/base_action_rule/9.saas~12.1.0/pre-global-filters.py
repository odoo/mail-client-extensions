# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Due to new rules, filters used by base action rules should not be bound to an user.
    cr.execute("""
        UPDATE ir_filters
           SET user_id = NULL
         WHERE id IN (SELECT filter_id
                        FROM base_action_rule
                       UNION
                      SELECT filter_pre_id
                        FROM base_action_rule)
    """)
