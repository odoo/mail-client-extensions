# -*- coding: utf-8 -*-


def migrate(cr, version):
    # rename the selection field [trigger_type] 'act' to 'activity'
    cr.execute(
        """
            UPDATE marketing_activity
               SET trigger_type = 'activity'
             WHERE trigger_type = 'act'
        """
    )
