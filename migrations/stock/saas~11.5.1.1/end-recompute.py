from odoo.addons.base.maintenance.migrations.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    # Necessary because translation is removed from stock.location.name
    # Check if multiple languages are installed befre triggering the recompute?
    # Overriding python compute for better performance:
    # https://github.com/odoo/odoo/blob/12.0/addons/stock/models/stock_location.py#L74
    break_recursive_loops(cr, "stock.location", "location_id")
    cr.execute("""
        WITH RECURSIVE location_hierarchy AS (
            SELECT id,
                   name AS complete_name
              FROM stock_location
             WHERE location_id IS NULL
             UNION ALL
            SELECT child.id,
                   parent.complete_name || '/' || child.name
              FROM stock_location child
              JOIN location_hierarchy parent
                ON child.location_id = parent.id
        )
        UPDATE stock_location
           SET complete_name = location_hierarchy.complete_name
          FROM location_hierarchy
         WHERE stock_location.id = location_hierarchy.id;
    """)
