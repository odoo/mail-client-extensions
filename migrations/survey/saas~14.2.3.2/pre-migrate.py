# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE survey_survey DROP CONSTRAINT IF EXISTS survey_survey_give_badge_check")
