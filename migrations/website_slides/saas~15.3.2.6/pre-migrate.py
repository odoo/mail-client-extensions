# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Limit vote value by sql constraint to -1, 0 or 1
    cr.execute(
        """
        UPDATE slide_slide_partner
           SET vote = COALESCE(SIGN(vote), 0)
         WHERE vote NOT IN (-1, 0, 1) OR vote IS NULL
        """
    )
