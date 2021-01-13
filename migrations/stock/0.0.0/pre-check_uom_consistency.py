# -*- coding: utf-8 -*-
import os
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~12.3"):
        fix_inconsistencies = os.environ.get("ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX")

        # if the customer absolutely wants to keep these inconsistencies as they are
        if fix_inconsistencies and fix_inconsistencies.upper() == "SKIP":
            return

        # if inconsistencies won't be fixed, get the faulty stock move lines
        if not fix_inconsistencies:
            cr.execute(
                """
                SELECT sml.move_id, array_agg(sml.id)
                  FROM stock_move_line sml
                  JOIN product_product pp ON pp.id = sml.product_id
                  JOIN product_template pt ON pt.id = pp.product_tmpl_id
                  JOIN uom_uom uom1 ON uom1.id = sml.product_uom_id
                  JOIN uom_uom uom2 ON uom2.id = pt.uom_id
                 WHERE uom1.category_id != uom2.category_id
                 GROUP BY sml.move_id
            """
            )
            if cr.rowcount:
                faulty_moves = ["%s (lines: %s)" % (str(move_id), str(lines)) for move_id, lines in cr.fetchall()]

        # then, fix inconsistencies (by keeping in mind that if fix_inconsistencies is not set,
        # an exception will be raised at the end to stop the upgrade).
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
        moves = ["%s (id: %s)" % (name, str(id)) for id, name in cr.fetchall() if id is not None]

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
        templates = ["%s (id: %s)" % (name, str(id)) for id, name in cr.fetchall()]

        if moves or templates:
            if fix_inconsistencies:
                move_details = (
                    "<h4>Stock moves</h4><ul>%s</ul>" % " ".join(["<li>%s</li>" % m for m in moves]) if moves else ""
                )
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
                            corresponding products. These inconsistencies lead to an
                            upgrade failure.
                            To avoid that failure, we have selected, for each product,
                            the most used UoM category in the corresponding stock moves.
                            Then, we have adapted the UoM of stock moves UoM and/or products if
                            they were not in this selected category.
                        </summary>
                        %s
                        %s
                    </details>
                    """
                    % (move_details, template_details),
                    category="Stock",
                    format="html",
                )
            else:
                raise util.MigrationError(
                    """
                    Some inconsistencies have been detected between the unit of measure (UoM) categories
                    used in some of your stock moves and the ones of the corresponding products.
                    So, you can:
                    - fix these inconsistencies manually (Here are the faulty stock moves: [%s])
                    OR
                    - ignore these inconsistencies and go on by setting the environment variable
                      ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX to SKIP
                    OR
                    - set the environment variable ODOO_MIG_ENABLE_UOM_INCONSISTENCIES_FIX to automatically
                    use the most used category. In this case, the following elements will be modified:
                        * stock moves : [%s]
                        * product templates : [%s]
                    """
                    % (", ".join(faulty_moves), ", ".join(moves), ", ".join(templates))
                )
