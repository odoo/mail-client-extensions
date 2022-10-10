# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS sale_subscription_report CASCADE")
