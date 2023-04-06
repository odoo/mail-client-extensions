# -*- coding: utf-8 -*-
import re
from uuid import uuid4

from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "ean13")

    # force product barcode in `barcode` field
    cr.execute(r"""UPDATE product_product p
                     SET barcode=p.default_code
                    FROM product_template t
                   WHERE t.id = p.product_tmpl_id
                     AND p.barcode IS NULL
                     AND p.default_code ~ '^\d+$'
                     AND t.available_in_pos=true
                     AND p.id NOT IN (
                        -- in 9.0, the barcodes should be unique
                        SELECT unnest(array_agg(id))
                          FROM product_product
                         WHERE default_code ~ '^\d+$'
                      GROUP BY default_code
                        HAVING count(id) > 1
                     )
               """)

    util.create_column(cr, 'pos_config', 'uuid', 'varchar')
    # NOTE can't use `uuid_generate_v4()`
    #    ERROR:  permission denied to create extension "uuid-ossp"
    #    HINT:  Must be superuser to create this extension.
    cr.execute('SELECT id FROM pos_config WHERE "uuid" IS NULL')
    for c, in cr.fetchall():
        cr.execute('UPDATE pos_config SET "uuid"=%s WHERE id=%s', [str(uuid4()), c])

    # convert pos_config.barcode_* field as a barcode.nomenclature

    util.create_column(cr, 'pos_config', 'barcode_nomenclature_id', 'int4')

    old_defaults = ('*', '041*', '042*', '21xxxxxNNDDD', '22xxxxxxxxNN', '23xxxxxNNNDD')
    new_default = util.ref(cr, 'barcodes.default_barcode_nomenclature')

    cr.execute("""SELECT barcode_product, barcode_cashier, barcode_customer,
                         barcode_weight, barcode_discount, barcode_price, array_agg(id) as ids
                    FROM pos_config
                   WHERE barcode_nomenclature_id IS NULL
                GROUP BY barcode_product, barcode_cashier, barcode_customer,
                         barcode_weight, barcode_discount, barcode_price
               """)
    for row in cr.fetchall():
        if row[:-1] == old_defaults:
            cr.execute("UPDATE pos_config SET barcode_nomenclature_id=%s WHERE id=ANY(%s)",
                       [new_default, row[-1]])
        else:
            # convert to rules
            def conv(code):
                code = code.replace('x', '.')
                code = re.sub(r'\*+', r'.*', code.rstrip('*'))
                code = re.sub(r'([ND]+)', r'{\1}', code)
                return code

            cr.execute("""INSERT INTO barcode_nomenclature (name, upc_ean_conv) VALUES(
                             'Auto nomenclature #' || (SELECT COUNT(1) + 1 FROM barcode_nomenclature),
                             'always')
                          RETURNING id
                       """)
            [nom_id] = cr.fetchone()

            types = 'product cashier client weight discount price'.split()
            for i, (type_, patterns) in enumerate(zip(types, row[:-1])):
                if not patterns:
                    patterns = old_defaults[i]
                sorted_by_digit_count = lambda x: len([c for c in x if c.isdigit()])
                patterns = sorted(patterns.split(','), key=sorted_by_digit_count, reverse=True)
                for j, p in enumerate(patterns):
                    seq = 120 - i * 20 + j      # will works for a max of 20 patterns per type
                    name = "%s Barcodes" % type_.title()
                    cr.execute("""INSERT INTO barcode_rule(name, barcode_nomenclature_id,
                                                           sequence, type, pattern,
                                                           encoding, alias)
                                       VALUES(%s, %s, %s, %s, %s, 'any', '0')
                               """, [name, nom_id, seq, type_, conv(p.strip())])

            cr.execute("""UPDATE pos_config
                             SET barcode_nomenclature_id = %s
                           WHERE id=ANY(%s)
                       """, [nom_id, row[-1]])
