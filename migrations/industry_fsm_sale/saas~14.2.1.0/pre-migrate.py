# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE project_project
           SET pricing_type = 'task_rate'
         WHERE is_fsm IS TRUE
        """
    )
