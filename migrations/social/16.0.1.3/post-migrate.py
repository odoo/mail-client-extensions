# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE social_media
        SET max_post_length = (
            CASE
                WHEN media_type = 'linkedin' THEN 3000
                WHEN media_type = 'twitter' THEN 280
                ELSE 0 END
            )
        """
    )
