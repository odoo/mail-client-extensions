# -*- coding: utf-8 -*-


def migrate(cr, version):

    cr.execute(
        """
    UPDATE stock_location l
       SET is_subcontracting_location = true
      FROM res_company c
      JOIN stock_location sl ON sl.id = c.subcontracting_location_id
     WHERE l.parent_path LIKE sl.parent_path || '%'
        """
    )
