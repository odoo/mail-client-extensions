# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("UPDATE res_company SET chart_template = 'ca_2023' WHERE chart_template = 'ca'")
