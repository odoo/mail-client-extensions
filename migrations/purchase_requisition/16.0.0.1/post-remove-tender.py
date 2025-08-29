from odoo.upgrade import util


def migrate(cr, version):
    _call_for_tender(cr)


def _call_for_tender(cr):
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

    util.add_to_migration_reports(
        """
            <p><strong>IMPORTANT NOTICE</strong></p>
            <p>
                The "Call for Tender" workflow changed in Odoo 16.
                Old Purchase agreements of type "Call for Tender" will be preserved
                for archival purposes but are DEPRECATED.
                Please do not use the old workflow and consult the
                documentation concerning the use of the "alternative" tab in Purchase Orders.
                Future changes of the purchase requisition model might lead to records
                being deleted or archived.
                See the <a href="https://www.odoo.com/event/odoo-experience-2022-2190/track/call-for-tenders-purchase-agreement-a-new-approach-in-odoo-16-4858"/>
                presentation made at Odoo Experience 2022</a> for more info.
            </p>
        """,
        category="Purchase Requisitions",
        format="html",
    )

    cr.execute("UPDATE purchase_requisition_type SET active='f' WHERE id = %s", [tender_id])
    util.force_noupdate(cr, "purchase_requisition.type_multi", noupdate=True)
