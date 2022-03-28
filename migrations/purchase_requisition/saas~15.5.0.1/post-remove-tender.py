# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    tender_id = util.ref(cr, "purchase_requisition.type_multi")
    if not tender_id:
        return

    # convert and delete call to tenders with linked POs (i.e. convert
    # to new implementation), but ignore the non-linked tenders so user
    # doesn't lose info
    cr.execute(
        """
        SELECT req.id, array_agg(po.id)
          FROM purchase_requisition req
          JOIN purchase_order po ON po.requisition_id = req.id
         WHERE req.type_id = %s
      GROUP BY req.id
        """,
        [tender_id],
    )

    reqs_to_pos = dict(cr.fetchall())
    if reqs_to_pos:
        env["purchase.order.group"].create(
            [{"order_ids": [(6, 0, po_ids)]} for po_ids in reqs_to_pos.values() if len(po_ids) > 1]
        )
        util.remove_records(cr, "purchase.requisition", reqs_to_pos.keys())

    cr.execute("UPDATE purchase_requisition_type SET active='f' WHERE id = %s", [tender_id])
    util.force_noupdate(cr, "purchase_requisition.type_multi", True)
