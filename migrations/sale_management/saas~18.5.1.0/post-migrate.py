from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_line", "_upg_new_sol", "bool")

    # 1. Insert "Optional Products" section line to sale_order_line
    so_insert_optional_section = """
        WITH so_to_upd AS (
            SELECT so.id
              FROM sale_order_option soo
              JOIN sale_order so
                ON so.id = soo.order_id
             WHERE so.state NOT IN ('sale', 'cancel')
               AND {parallel_filter}
          GROUP BY so.id
        ),
        sol_max AS (
            SELECT l.order_id,
                   MAX(l.sequence) AS max_seq
              FROM sale_order_line l
              JOIN sale_order so
                ON so.id = l.order_id
             WHERE {parallel_filter}
          GROUP BY order_id
        )
        INSERT INTO sale_order_line (
                    order_id, create_uid, create_date, write_uid, write_date,
                    currency_id, order_partner_id, salesman_id, state,
                    sequence, display_type, name,
                    company_id, is_optional, product_uom_qty, price_unit, customer_lead
                    )
             SELECT so.id, so.create_uid, so.create_date, so.write_uid, so.write_date,
                    so.currency_id, so.partner_id, so.user_id, so.state,
                    COALESCE(sol_max.max_seq, 0) + 1, 'line_section', 'Optional Products',
                    so.company_id, True, 0, 0.0, 0.0
               FROM sale_order AS so
               JOIN so_to_upd
                 ON so_to_upd.id = so.id
          LEFT JOIN sol_max
                 ON sol_max.order_id = so.id
    """

    util.explode_execute(cr, so_insert_optional_section, table="sale_order", alias="so")

    # 2. Move "Optional Products" related sale_order_line to optional section
    move_option_related_sol = """
        WITH max_seq AS (
            SELECT
                so.id AS order_id,
                MAX(sol.sequence) AS max_sequence
              FROM sale_order_line sol
              JOIN sale_order so
                ON so.id = sol.order_id
          WHERE so.state NOT IN ('sale', 'cancel')
               AND {parallel_filter}
          GROUP BY so.id
        ),
        target AS (
            SELECT
                soo.line_id,
                sol.order_id,
                ms.max_sequence
            FROM sale_order_option soo
            JOIN sale_order_line sol ON sol.id = soo.line_id
            JOIN max_seq ms ON ms.order_id = sol.order_id
        )
        UPDATE sale_order_line sol
           SET sequence = t.max_sequence + 1,
               is_optional = True
          FROM target t
         WHERE sol.id = t.line_id
    """

    util.explode_execute(cr, move_option_related_sol, table="sale_order", alias="so")

    # 3. Insert optional lines in the "Optional Products" section
    so_insert_optional_lines = """
        INSERT INTO sale_order_line (
                    create_uid, create_date, write_uid, write_date, order_id,
                    price_unit, technical_price_unit, name, product_id,
                    product_uom_qty, product_uom_id, discount,
                    company_id, currency_id, order_partner_id,
                    salesman_id, state, is_optional, customer_lead, _upg_new_sol,
                    sequence
                    )
             SELECT soo.create_uid, soo.create_date, soo.write_uid, soo.write_date, soo.order_id,
                    soo.price_unit, soo.price_unit AS technical_price_unit, soo.name, soo.product_id,
                    0.0, soo.uom_id AS product_uom_id, soo.discount,
                    section.company_id, section.currency_id, section.order_partner_id,
                    section.salesman_id, section.state, True, 0.0, True,
                    section.sequence + ROW_NUMBER() OVER (PARTITION BY soo.order_id ORDER BY soo.id)
               FROM sale_order_option AS soo
               JOIN sale_order AS so
                 ON so.id = soo.order_id
               JOIN sale_order_line AS section
                 ON section.order_id = soo.order_id
                 AND section.display_type = 'line_section'
                 AND section.is_optional
              WHERE so.state NOT IN ('sale', 'cancel')
                 AND soo.line_id IS NULL
                 AND {parallel_filter}
        """

    util.explode_execute(cr, so_insert_optional_lines, table="sale_order", alias="so")

    util.remove_field(cr, "sale.order.line", "sale_order_option_ids")
    util.remove_field(cr, "sale.order", "sale_order_option_ids")
    util.remove_model(cr, "sale.order.option")

    # 4. Insert "Optional Products" section line to sale_order_template_line
    sot_insert_optional_section = """
        WITH sot_to_upd AS (
            SELECT sot.id
              FROM sale_order_template_option soto
              JOIN sale_order_template sot
                ON sot.id = soto.sale_order_template_id
             WHERE {parallel_filter}
          GROUP BY sot.id
        ),
        sotl_max AS (
            SELECT l.sale_order_template_id,
                   MAX(l.sequence) AS max_seq
              FROM sale_order_template_line l
              JOIN sale_order_template sot
                ON sot.id = l.sale_order_template_id
             WHERE {parallel_filter}
          GROUP BY sale_order_template_id
        )
        INSERT INTO sale_order_template_line (
                    sale_order_template_id, create_uid, create_date, write_uid, write_date,
                    sequence, display_type,
                    name, company_id, product_uom_qty, is_optional
                    )
             SELECT sot.id, sot.create_uid, sot.create_date, sot.write_uid, sot.write_date,
                    COALESCE(sotl_max.max_seq, 0) + 1, 'line_section',
                    jsonb_build_object('en_US', 'Optional Products'), sot.company_id, 0, True
               FROM sale_order_template AS sot
               JOIN sot_to_upd
                 ON sot_to_upd.id = sot.id
          LEFT JOIN sotl_max
                 ON sotl_max.sale_order_template_id = sot.id
    """

    util.explode_execute(cr, sot_insert_optional_section, table="sale_order_template", alias="sot")

    # 5. Insert optional template lines after the "Optional Products" section
    sot_insert_optional_lines = """
        INSERT INTO sale_order_template_line (
                    sale_order_template_id, name, product_id,
                    product_uom_qty, product_uom_id, create_uid,
                    create_date, write_uid, write_date, company_id,
                    sequence
                    )
             SELECT soto.sale_order_template_id, soto.name, soto.product_id,
                    soto.quantity AS product_uom_qty, soto.uom_id AS product_uom_id, soto.create_uid,
                    soto.create_date, soto.write_uid, soto.write_date, soto.company_id,
                    section.sequence + ROW_NUMBER() OVER (
                       PARTITION BY soto.sale_order_template_id
                       ORDER BY soto.id
                   )
               FROM sale_order_template_option AS soto
               JOIN sale_order_template AS sot
                 ON sot.id = soto.sale_order_template_id
               JOIN sale_order_template_line AS section
                 ON section.sale_order_template_id = soto.sale_order_template_id
              WHERE section.display_type = 'line_section'
                 AND section.is_optional
                 AND {parallel_filter}
    """

    util.explode_execute(cr, sot_insert_optional_lines, table="sale_order_template", alias="sot")

    util.remove_field(cr, "sale.order.template", "sale_order_template_option_ids")
    util.remove_model(cr, "sale.order.template.option")
