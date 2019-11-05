# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def parent_path(cr, model, parent_name='parent_id'):
    table = util.table_of_model(cr, model)
    if not util.column_exists(cr, table, parent_name):
        return
    util.create_column(cr, table, 'parent_path', 'varchar')
    util.remove_field(cr, model, 'parent_left')
    util.remove_field(cr, model, 'parent_right')

    cr.execute("""
        WITH RECURSIVE __parent_store_compute(id, parent_path) AS (
            SELECT row.id, concat(row.id, '/')
            FROM {table} row
            WHERE row.{parent} IS NULL
        UNION
            SELECT row.id, concat(comp.parent_path, row.id, '/')
            FROM {table} row, __parent_store_compute comp
            WHERE row.{parent} = comp.id
        )
        UPDATE {table} row SET parent_path = comp.parent_path
        FROM __parent_store_compute comp
        WHERE row.id = comp.id
    """.format(table=table, parent=parent_name))

def migrate(cr, version):
    parents = util.splitlines("""
        ir.ui.menu
        res.partner.category

        test_new_api.category:parent

        account.group
        account.analytic.group
        product.category
        stock.location:location_id
        website.menu
        forum.documentation.toc

        account.financial.html.report.line
    """)
    for model in parents:
        model, _, parent_name = model.partition(':')
        parent_path(cr, model, parent_name or 'parent_id')
