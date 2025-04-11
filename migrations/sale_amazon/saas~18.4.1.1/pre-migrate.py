from odoo.upgrade import util


def migrate(cr, version):
    # Move the old `is_fbm` "field" to `amazon_channel` and compute `sync_stock`
    util.create_column(cr, "amazon_offer", "sync_stock", "boolean")
    util.create_column(cr, "amazon_offer", "amazon_channel", "varchar")
    cr.execute(
        """
        WITH parsed_offers AS (
            SELECT o.id,
                   CASE
                   WHEN jsonb_typeof(amazon_feed_ref::jsonb) = 'object' THEN (amazon_feed_ref::jsonb->'is_fbm')::boolean
                   ELSE NULL
                   END AS is_fbm,
                   a.synchronize_inventory,
                   pt.is_storable
              FROM amazon_offer o
              JOIN amazon_account a
                ON o.account_id = a.id
              JOIN product_template pt
                ON o.product_template_id = pt.id
        )
        UPDATE amazon_offer o
           SET amazon_feed_ref = CASE
                                 WHEN po.is_fbm IS NOT NULL THEN (amazon_feed_ref::jsonb - 'is_fbm')::varchar
                                 ELSE amazon_feed_ref
                                 END,
                amazon_channel = CASE
                                 WHEN po.is_fbm THEN 'fbm'
                                 WHEN po.is_fbm IS FALSE THEN 'fba'
                                 ELSE NULL
                                 END,
                    sync_stock = po.synchronize_inventory AND po.is_storable AND (po.is_fbm IS NULL OR po.is_fbm)
          FROM parsed_offers po
         WHERE o.id = po.id
        """,
    )
