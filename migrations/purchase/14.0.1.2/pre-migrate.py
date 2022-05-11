# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Now a dynamic view. See https://github.com/odoo/odoo/pull/75651
    cr.execute("DROP VIEW IF EXISTS purchase_report")
