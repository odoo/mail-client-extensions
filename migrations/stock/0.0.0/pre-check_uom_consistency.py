# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def fix_moves(cr):
    """
    Fix stock move lines based on the previously computed main_uoms table.
    See different available methods below.
    """
    cr.execute(
        """
           UPDATE stock_move_line sml
              SET product_uom_id = mu.main_uom_id
             FROM main_uoms mu, uom_uom uom, product_product pp, stock_move sm
            WHERE pp.id = sml.product_id
              AND mu.tmpl_id = pp.product_tmpl_id
              AND uom.id = sml.product_uom_id
              AND uom.category_id != mu.main_categ_id
              AND (sm.id = sml.move_id OR sml.move_id IS NULL)
        RETURNING sml.move_id, sm.name
        """
    )
    return ["%s (id: %s)" % (name, str(id)) for id, name in cr.fetchall() if id is not None]


def fix_product_templates(cr):
    """
    Fix product templates based on the previously computed main_uoms table.
    See different available methods below.
    """
    cr.execute(
        """
           UPDATE product_template pt
              SET uom_id = mu.main_uom_id
             FROM uom_uom uom, main_uoms mu
            WHERE pt.id = mu.tmpl_id
              AND uom.id = pt.uom_id
              AND uom.category_id != mu.main_categ_id
        RETURNING pt.id, pt.name
        """
    )
    return ["%s (id: %s)" % (name, str(id)) for id, name in cr.fetchall()]


def fix_with_most_used_method(cr):
    """
    Fix stock move lines and product templates using the most used UoM category.
    """
    cr.execute(
        """
        -- select product templates where stock move line UoM category differs from product UoM category
        WITH product_templates AS (
            SELECT distinct pt.id
              FROM stock_move_line sml
              JOIN product_product pp ON pp.id = sml.product_id
              JOIN product_template pt ON pt.id = pp.product_tmpl_id
              JOIN uom_uom uom1 ON uom1.id = sml.product_uom_id
              JOIN uom_uom uom2 ON uom2.id = pt.uom_id
             WHERE uom1.category_id != uom2.category_id
               AND pp.active = true
        ),

        -- for each product templates, get the main UoM category used in stock move lines
        main_categories AS (
            SELECT DISTINCT ON (tmpl_id) tmpl_id, uom_category_id
                FROM (
                    SELECT pt.id AS tmpl_id, uom.category_id AS uom_category_id
                      FROM stock_move_line sml
                      JOIN product_product pp ON pp.id = sml.product_id
                      JOIN product_templates pt ON pt.id = pp.product_tmpl_id
                      JOIN uom_uom uom ON uom.id = sml.product_uom_id
                  GROUP BY pt.id, uom.category_id
                  ORDER BY pt.id, COUNT(uom.category_id) DESC, uom.category_id
            ) as rows
        )

        -- for each product templates, get the main UoM of the main UoM category used in stock move lines
        SELECT DISTINCT ON (tmpl_id) tmpl_id, product_uom_id AS main_uom_id, category_id AS main_categ_id
            INTO TEMPORARY main_uoms
            FROM (
                  SELECT mc.tmpl_id, sml.product_uom_id, uom.category_id
                    FROM stock_move_line sml
                    JOIN product_product pp ON pp.id = sml.product_id
                    JOIN main_categories mc ON mc.tmpl_id = pp.product_tmpl_id
                    JOIN uom_uom uom ON uom.id = sml.product_uom_id AND uom.category_id = mc.uom_category_id
                GROUP BY mc.tmpl_id,  uom.category_id, sml.product_uom_id
                ORDER BY mc.tmpl_id, uom.category_id, COUNT(sml.product_uom_id) DESC, sml.product_uom_id
        ) as rows
    """
    )
    moves = fix_moves(cr)
    templates = fix_product_templates(cr)
    log_customer_report(
        cr,
        explanation="""
            To avoid that failure, we have selected, for each product,
            the most used UoM category in the corresponding stock moves.
            Then, we have adapted the UoM of stock moves UoM and/or products if
            they were not in this selected category.
        """,
        moves=moves,
        templates=templates,
    )


def fix_with_from_product_method(cr):
    """
    Fix stock move lines using the UoM of the corresponding product.
    """
    cr.execute(
        """
        SELECT distinct pt.id AS tmpl_id, pt.uom_id AS main_uom_id, uom2.category_id AS main_categ_id
          INTO TEMPORARY main_uoms
          FROM product_template pt
          JOIN product_product pp ON pp.product_tmpl_id = pt.id
          JOIN stock_move_line sml ON sml.product_id = pp.id
          JOIN uom_uom uom1 ON uom1.id = sml.product_uom_id
          JOIN uom_uom uom2 ON uom2.id = pt.uom_id
         WHERE uom1.category_id != uom2.category_id
           AND pp.active = true
        """
    )
    moves = fix_moves(cr)
    log_customer_report(
        cr,
        explanation="""
            To avoid that failure, we have updated all the faulty stock moves with
            the UoM of the corresponding product.
        """,
        moves=moves,
    )


def log_customer_report(cr, explanation, moves=None, templates=None):
    """
    Add an explanation of modified objects to the customer report.
    """
    if moves or templates:
        move_details = "<h4>Stock moves</h4><ul>%s</ul>" % " ".join(["<li>%s</li>" % m for m in moves]) if moves else ""
        template_details = (
            "<h4>Product templates</h4><ul>%s</ul>" % " ".join(["<li>%s</li>" % t for t in templates])
            if templates
            else ""
        )

        util.add_to_migration_reports(
            message="""
            <details>
                <summary>
                    While upgrading your database, we have detected some
                    inconsistencies between the unit of measure (UoM) categories
                    used in some of your stock moves and the ones of the
                    corresponding products. These inconsistencies may lead to an
                    upgrade failure.
                    %s
                </summary>
                %s
                %s
            </details>
            """
            % (explanation, move_details, template_details),
            category="Stock",
            format="html",
        )


def log_faulty_objects(cr):
    """
    In case no fixing method has been chosen, stop the migration with the
    list of faulty moves to inform the customer.
    """
    cr.execute(
        """
          SELECT sml.move_id, array_agg(sml.id)
            FROM stock_move_line sml
            JOIN product_product pp ON pp.id = sml.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN uom_uom uom1 ON uom1.id = sml.product_uom_id
            JOIN uom_uom uom2 ON uom2.id = pt.uom_id
           WHERE uom1.category_id != uom2.category_id
             AND pp.active = true
        GROUP BY sml.move_id
        """
    )
    faulty_moves = ["%s (lines: %s)" % (str(move_id), str(lines)) for move_id, lines in cr.fetchall()]

    if faulty_moves:
        raise util.MigrationError(
            """
            Some inconsistencies have been detected between the unit of measure (UoM) categories
            used in some of your stock moves and the ones of the corresponding products.
            So, you can:
            - fix these inconsistencies manually (Here are the faulty stock moves):
            %s
            OR
            - ignore these inconsistencies and go on by setting the environment variable
                ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX to SKIP
            OR
            - set the environment variable ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX to one of the
            automatic fixes:
                * MOST_USED: to automatically use the most used category,
                * FROM_PRODUCT: to automatically use the UoM from the product
            """
            % ("\n".join(["                * %s" % sm for sm in faulty_moves]),)
        )


def migrate(cr, version):
    if not util.version_gte("saas~12.3"):
        return

    # Handle inconsistencies between UoM category used in stock move lines and the
    # one configured on the corresponding product template.
    # There are several solutions depending on the value of the environment variable
    # ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX:
    # - not set: a fatal failure is raised and show information about these inconsistencies,
    # - SKIP: the customer assumes these inconsistencies and wants to keep them,
    # - MOST_USED: select, for each product template, the most used UoM category in stock moves
    #              and update stock moves/product templates with it.
    # - FROM_PRODUCT: update all the stock moves to use the UoM set on the product template
    allowed_methods = ["SKIP", "MOST_USED", "FROM_PRODUCT"]
    fix_inconsistencies_method = os.environ.get("ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX", "").upper()

    if fix_inconsistencies_method and fix_inconsistencies_method not in allowed_methods:
        raise ValueError(
            "unknown value for environment variable ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX: %s"
            % fix_inconsistencies_method
        )

    if fix_inconsistencies_method == "SKIP":
        # if the customer absolutely wants to keep these inconsistencies as they are
        return
    elif fix_inconsistencies_method == "MOST_USED":
        fix_with_most_used_method(cr)
    elif fix_inconsistencies_method == "FROM_PRODUCT":
        fix_with_from_product_method(cr)
    else:
        log_faulty_objects(cr)
