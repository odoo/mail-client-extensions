# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM mailing_trace WHERE res_id = 0")
