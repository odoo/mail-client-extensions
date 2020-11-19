# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_act_server a
           SET model_name = m.model
          FROM ir_model m
         WHERE a.model_id = m.id
           AND a.model_name != m.model
        """
    )
