# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_lang rl
           SET active = true
          FROM res_partner rp
         WHERE rl.code = rp.lang
           AND rl.active = false
    """
    )
