# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("UPDATE account_analytic_line SET name='/' WHERE name IS NULL")
