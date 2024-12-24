def migrate(cr, version):
    # This file is symlinked in saas~18.1.1.3 for the dbs that were already upgraded to v18.
    cr.execute(
        """
        UPDATE res_partner_category
           SET parent_path = CONCAT(id, '/')
         WHERE parent_path IS NULL
        """
    )
