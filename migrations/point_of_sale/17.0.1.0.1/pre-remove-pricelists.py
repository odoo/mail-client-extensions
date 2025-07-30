from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE pos_config AS c
           SET use_pricelist = False
          FROM product_pricelist AS p
         WHERE c.pricelist_id = p.id
           AND NOT p.active
     RETURNING c.id, c.name, c.active
        """
    )
    configs = [
        f"<li>{util.get_anchor_link_to_record('pos.config', id, name)}</li>"
        for id, name, active in cr.fetchall()
        if active
    ]
    if configs:
        util.add_to_migration_reports(
            f"""
            <details>
                <summary>
                    The following PoS configs no longer use pricelists
                    as their corresponding pricelists are archived.
                </summary>
                <ul>{"".join(configs)}</ul>
            </details>
            """,
            "Point of Sale",
            format="html",
        )
