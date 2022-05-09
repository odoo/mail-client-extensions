# -*- coding: utf-8 -*-


def migrate(cr, version):
    # A uom of type 'reference' is necessary per category.
    # If it's missing, it will raise an error when trying to update a record.
    # This file is symlinked in saas~15.1.1.0 for the dbs that were already upgraded to v15.
    cr.execute(
        """
        INSERT INTO uom_uom
               (name, category_id, factor, rounding, active, uom_type, create_date, create_uid)
        SELECT 'Reference Unit', c.id, 1.0, 0.01, True, 'reference', c.create_date, c.create_uid
          FROM uom_category AS c
         WHERE NOT EXISTS(
                    SELECT 1
                      FROM uom_uom AS u
                     WHERE u.category_id = c.id
                       AND u.uom_type = 'reference'
                   )
        """
    )
