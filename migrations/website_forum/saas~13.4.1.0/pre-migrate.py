# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE forum_post_reason
           SET reason_type = 'basic'
         WHERE reason_type NOT IN ('basic', 'offensive')
    """
    )
