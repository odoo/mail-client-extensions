# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Create fleets from what we have
    cr.execute(
        """
           INSERT INTO fleet_category (
                       name,
                       manager_id,
                       company_id,
                       active,
                       create_uid,
                       write_uid,
                       create_date,
                       write_date
                )
                SELECT concat(pt.name, '''s Fleet') AS name,
                       ve.manager_id,
                       ve.company_id,
                       TRUE as active,
                       1 as create_uid,
                       1 as write_uid,
                       now() at time zone 'utc',
                       now() at time zone 'utc'
                  FROM fleet_vehicle ve
            INNER JOIN res_users us ON ve.manager_id = us.id
            INNER JOIN res_partner pt ON us.partner_id = pt.id
                 WHERE ve.manager_id IS NOT NULL
              GROUP BY ve.manager_id, pt.name, ve.company_id
    """
    )

    # Add to favorite by default, ignore duplicate key errors
    cr.execute(
        """
   INSERT INTO fleet_category_res_users_rel (
               fleet_category_id,
               res_users_id
        )
        SELECT fc.id as fleet_category_id,
               fc.manager_id as res_users_id
          FROM fleet_category fc
         WHERE fc.manager_id IS NOT NULL
           AND NOT EXISTS (SELECT 1
                             FROM fleet_category_res_users_rel r
                            WHERE r.fleet_category_id=fc.id
                              AND r.res_users_id=fc.manager_id)
    """
    )

    # Insert fleet ID's from previously created entries
    cr.execute(
        """
        UPDATE fleet_vehicle v
           SET fleet_id = fl.id
          FROM fleet_category fl
         WHERE fl.manager_id = v.manager_id
           AND fl.company_id IS NOT DISTINCT FROM v.company_id
    """
    )
