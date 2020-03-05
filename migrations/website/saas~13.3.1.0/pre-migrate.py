# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS website_visitor_partner_rel")
