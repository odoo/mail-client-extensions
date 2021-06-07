# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM mailing_trace WHERE model IS NULL OR res_id IS NULL")
