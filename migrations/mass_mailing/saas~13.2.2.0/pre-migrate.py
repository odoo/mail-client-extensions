# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM mailing_mailing WHERE mailing_model_id IS NULL")
