from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.inconsistencies.break_recursive_loops(cr, "product.category", "parent_id")
    util.create_column(cr, "product_category", "complete_name", "varchar")
    cr.execute(
        """
        WITH RECURSIVE data AS (
            SELECT id,
                   name AS complete_name
              FROM product_category
             WHERE parent_id IS NULL
             UNION ALL
            SELECT category.id,
                   parent.complete_name || ' / ' || category.name
              FROM product_category AS category
              JOIN data AS parent
                ON category.parent_id = parent.id
        )
        UPDATE product_category
           SET complete_name = data.complete_name
          FROM data
         WHERE data.id = product_category.id
        """
    )

    util.create_column(cr, "product_template", "activity_date_deadline", "date")
    util.explode_execute(
        cr,
        """
        WITH deadlines AS (
            SELECT a.res_id,
                   MIN(a.date_deadline) AS date
              FROM mail_activity a
              JOIN product_template t
                ON a.res_model = 'product.template'
               AND a.res_id = t.id
             WHERE {parallel_filter}
          GROUP BY a.res_id
        )
        UPDATE product_template
           SET activity_date_deadline = deadlines.date
          FROM deadlines
         WHERE product_template.id = deadlines.res_id
        """,
        table="product_template",
        alias="t",
    )

    util.create_column(cr, "product_product", "activity_date_deadline", "date")
    util.explode_execute(
        cr,
        """
        WITH deadlines AS (
            SELECT a.res_id,
                   MIN(a.date_deadline) AS date
              FROM mail_activity a
              JOIN product_product p
                ON a.res_model = 'product.product'
               AND a.res_id = p.id
             WHERE {parallel_filter}
          GROUP BY a.res_id
        )
        UPDATE product_product
           SET activity_date_deadline = deadlines.date
          FROM deadlines
         WHERE product_product.id = deadlines.res_id
        """,
        table="product_product",
        alias="p",
    )
