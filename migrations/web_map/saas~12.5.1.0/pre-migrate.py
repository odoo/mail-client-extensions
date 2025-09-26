from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "contact_address_complete", "varchar")
    util.explode_execute(
        cr,
        """
        WITH _p AS (
            SELECT p.id, p.street, p.zip, p.city, c.name
              FROM res_partner p
         LEFT JOIN res_country c ON c.id = p.country_id
             WHERE {parallel_filter}
               AND p.contact_address_complete IS NULL
        )
        UPDATE res_partner p
           SET contact_address_complete = CONCAT(
               _p.street, ', ', _p.zip, ' ', _p.city, ', ', _p.name
           )
          FROM _p
         WHERE _p.id = p.id
        """,
        table="res_partner",
        alias="p",
    )
