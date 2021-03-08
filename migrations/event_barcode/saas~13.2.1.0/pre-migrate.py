# -*- coding: utf-8 -*-
import random

from odoo.upgrade import util


def migrate(cr, version):
    idx = util.get_index_on(cr, "event_registration", "barcode", "event_id")
    if idx:
        if idx.isunique and not idx.ispk:
            idx.drop(cr)

    # now deduplicate barcodes
    cr.execute(
        """
        SELECT unnest((array_agg(id ORDER BY id))[2:])
          FROM event_registration
         WHERE barcode IS NOT NULL
      GROUP BY barcode
    """
    )

    queries = [
        cr.mogrify("UPDATE event_registration SET barcode=%s WHERE id=%s", [random.getrandbits(64), rid])
        for rid, in cr.fetchall()
    ]

    util.parallel_execute(cr, queries)
