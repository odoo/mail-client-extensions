# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            UPDATE hr_skill_level
               SET level_progress = GREATEST(LEAST(level_progress, 100), 0)
             WHERE level_progress NOT BETWEEN 0 AND 100
        """
    )
