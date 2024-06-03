import logging
import os

from psycopg2.extras import execute_values

from odoo.tools import flatten

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.product.saas-12.5." + __name__)


def migrate(cr, version):
    "Handle the case where there are many product_products with the same template"

    cr.execute(
        """
        SELECT product_tmpl_id, combination_indices, array_agg(id) ids, count(*) cnt
          FROM product_product
         WHERE active
      GROUP BY product_tmpl_id, combination_indices
        HAVING COUNT(*)>1
        """
    )
    problematic_templates = cr.dictfetchall()

    if not problematic_templates:
        return
    distinct_products = flatten(i["ids"] for i in problematic_templates)
    if util.str2bool(os.environ.get("MIG_13_ARCHIVE_DUPLICATE_PRODUCT"), default=False):
        _logger.info("Duplicate variant with same attributes, solved by archiving")

        referenced = {k: 0 for k in distinct_products}
        # loop through all tables to get the number of rows referenced for each product
        for tbl, col, _, _ in util.get_fk(cr, "product_product"):
            cr.execute(
                f"SELECT {col} AS id, count(*) cnt FROM {tbl} WHERE {col} =ANY(%s) GROUP BY 1", [distinct_products]
            )
            for r in cr.dictfetchall():
                referenced[r["id"]] += r["cnt"]

        product_to_archive = []
        for problematic_row in problematic_templates:
            referenced_filtered = {k: v for k, v in referenced.items() if k in problematic_row["ids"]}
            referenced_filtered.pop(max(referenced_filtered, key=referenced_filtered.get))
            product_to_archive.extend(list(referenced_filtered))

        cr.execute("UPDATE product_product pp SET active='f' WHERE id =ANY(%s)", (product_to_archive,))
        msg = """In our standard, all variant of the same product needs to have distinct attributes to ensure data integrity.
In your database, we detected that you have variant(s) for the same product with the same attributes (or no attributes);
Hence we archived {archived_product_count} variants, as a matter of fact, archiving the variant is the default way to solve the problem.
You can reactivate the variants in your database by accessing your variant configuration panel;
Alternatively, you can:
- either fix the issue in you original database (before the upgrade request)
- or fix the issue automatically by adding the 'technical' attributes on conflicting variants.
To automatically set 'technical' attributes during the upgrade, please contact the support (https://www.odoo.com/help) (a new migration is required)
The following variants has been archived: {archived_product_list}""".format(
            archived_product_count=str(len(product_to_archive)),
            archived_product_list=",".join([str(p) for p in product_to_archive]),
        )
        _logger.info(msg)
        util.add_to_migration_reports(msg)
    else:
        _logger.info("Duplicate variant with same attributes, solved by adding technical attributes")
        # Alternative choice, Add a new technical attribute to conflicting variants
        max_variant_to_create = max(i["cnt"] for i in problematic_templates)
        distinct_templates = {i["product_tmpl_id"] for i in problematic_templates}

        # create a new product_attribute
        if util.column_exists(cr, "product_attribute", "type"):
            cr.execute(
                """
                INSERT INTO product_attribute (name, create_variant, type)
                     VALUES ('odoo_technical','dynamic','radio')
                  RETURNING id
                """
            )
        else:
            cr.execute(
                """
                INSERT INTO product_attribute (name, create_variant)
                     VALUES ('odoo_technical','dynamic')
                  RETURNING id
                """
            )

        created_product_attribute = cr.fetchone()[0]

        # Create all the needed product_attribute_value
        # variant value contains 'upgrade_technical'.
        # So it is possible to find them easily in the odoo interface
        cr.execute(
            """
            INSERT INTO product_attribute_value ("name", "sequence", attribute_id)
                 SELECT concat('upgrade_', gs::varchar), gs, %s
                  FROM (SELECT generate_series(1, %s) gs) x
             RETURNING id
             """,
            [created_product_attribute, max_variant_to_create],
        )
        created_product_attribute_values = [i["id"] for i in cr.dictfetchall()]

        product_template_attribute_line_ids = {}
        for template in distinct_templates:
            cr.execute(
                """
                INSERT INTO product_template_attribute_line (active, product_tmpl_id, attribute_id)
                    VALUES (true, %s, %s)
                 RETURNING id
                 """,
                [template, created_product_attribute],
            )
            created_attribute_line = cr.fetchone()[0]
            insert_tuples_query1 = []
            insert_tuples_query2 = []
            for i in range(max_variant_to_create):
                # optimization, prepare the inserts, insert in one query
                insert_tuples_query1.append(
                    (
                        True,
                        created_product_attribute_values[i],
                        created_attribute_line,
                        0.00,
                        template,
                        created_product_attribute,
                    )
                )
                insert_tuples_query2.append((created_attribute_line, created_product_attribute_values[i]))
            execute_values(
                cr._obj,
                """
                INSERT INTO product_template_attribute_value
                            (ptav_active, product_attribute_value_id, attribute_line_id,
                            price_extra, product_tmpl_id, attribute_id)
                     VALUES %s
                  RETURNING id
                  """,
                insert_tuples_query1,
                page_size=max_variant_to_create,
            )
            product_template_attribute_line_ids[template] = [i["id"] for i in cr.dictfetchall()]

            execute_values(
                cr._obj,
                """
                INSERT INTO product_attribute_value_product_template_attribute_line_rel
                            (product_template_attribute_line_id, product_attribute_value_id)
                     VALUES %s
                     """,
                insert_tuples_query2,
            )

        insert_tuples_query3 = []
        for template in problematic_templates:
            tmpl_id = template["product_tmpl_id"]
            related_product_template_attribute_line_ids = product_template_attribute_line_ids[tmpl_id]
            for i, product_product in enumerate(template["ids"]):
                # optimization, prepare the inserts, insert in one query
                insert_tuples_query3.append((product_product, related_product_template_attribute_line_ids[i]))
        execute_values(
            cr._obj,
            """
            INSERT INTO product_variant_combination (product_product_id, product_template_attribute_value_id)
                 VALUES %s
            """,
            insert_tuples_query3,
        )

        # Recompute combination_indices only for the touched products
        # Normally only the with clause is needed
        cr.execute(
            """
            WITH updated AS
            (
                UPDATE product_product a SET combination_indices=b.new_combination_indices
                FROM
                (
                    SELECT product_product_id, string_agg(product_template_attribute_value_id::varchar, ',') new_combination_indices
                      FROM product_variant_combination
                  GROUP BY product_product_id
                ) b
                WHERE a.id = b.product_product_id
                  AND a.id =ANY(%s)
            RETURNING b.product_product_id AS id
            )
            UPDATE product_product a SET combination_indices=''
             WHERE a.id =ANY(%s)
               AND a.id NOT IN (SELECT id FROM updated)""",
            [distinct_products, distinct_products],
        )

        # clean product_attribute_value_product_template_attribute_line_rel m2m
        util.fixup_m2m(
            cr,
            m2m="product_attribute_value_product_template_attribute_line_rel",
            fk1="product_attribute_value",
            fk2="product_template_attribute_line",
            col1="product_attribute_value_id",
            col2="product_template_attribute_line_id",
        )

        # log a note to the end user
        msg = """ In our standard, all variant of the same product needs to have distinct attributes to ensure data integrity;  In your database, we detected that you have variant(s) for the same product with the same attributes (or no attributes).
Hence we updated your variant attributes and added the`upgrade_technical` attribute, enabling the eligibility of your database (same product same attribute) for our upgrade scripts (same product, distinct attribute) without issues;
You can find these `upgrade_technical` attributes in your database by navigating to your Settings App > General Settings > searching on 'Variants and Options' and clicking on 'Attributes'
Alternatively, you can:
- either fix the issue in you original database (before the upgrade request)
- or fix the issue automatically by archiving the less used variants (loop through tables and count rows referencing this product (using foreign keys)).
To automatically 'archive variants' during the upgrade, please contact the support (https://www.odoo.com/help) (a new migration is required)"""
        _logger.info(msg)
        util.add_to_migration_reports(msg)
