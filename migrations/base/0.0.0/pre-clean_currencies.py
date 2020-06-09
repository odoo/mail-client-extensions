# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM res_currency_rate WHERE COALESCE(rate, 0) <= 0.0")
