from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "product.template", "self_order_visible", selectable=False)

    query = """
        UPDATE pos_order
              SET source = CASE
                      WHEN pos_reference LIKE '%Kiosk%' THEN 'kiosk'
                      WHEN pos_reference LIKE '%Self-Order%' THEN 'mobile'
                      ELSE source
                  END
            WHERE pos_reference LIKE ANY(ARRAY['%Kiosk%', '%Self-Order%'])
    """
    util.explode_execute(cr, query, table="pos_order")
