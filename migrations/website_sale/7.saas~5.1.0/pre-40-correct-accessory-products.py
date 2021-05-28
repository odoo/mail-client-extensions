# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """SELECT cl2.relname
                    FROM pg_constraint cn
                    JOIN pg_class cl1 on cl1.oid = cn.conrelid
                    JOIN pg_class cl2 on cl2.oid = cn.confrelid
                   WHERE cl1.relname = 'product_accessory_rel'
                     AND cn.conname = 'product_accessory_rel_dest_id_fkey'
               """
    )

    [relname] = cr.fetchone() or [None]
    if relname == "product_product":
        return  # already correct

    cr.execute(
        """ALTER TABLE product_accessory_rel
              DROP CONSTRAINT product_accessory_rel_dest_id_fkey
               """
    )

    cr.execute(
        """UPDATE product_accessory_rel r
                     SET dest_id=(SELECT id
                                    FROM product_product
                                   WHERE product_tmpl_id = r.dest_id
                                ORDER BY id ASC
                                   LIMIT 1)
               """
    )

    cr.execute(
        """ALTER TABLE product_accessory_rel
               ADD CONSTRAINT product_accessory_rel_dest_id_fkey
                  FOREIGN KEY (dest_id)
                   REFERENCES product_product(id)
                    ON DELETE CASCADE
               """
    )
