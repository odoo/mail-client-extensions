# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_attachment
           SET url = '/'||url
         WHERE type='url'
           AND url ilike 'theme_%'
           AND res_model = 'ir.module.module'
    """
    )
