# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~12.5"):
        # This no longer applies since odoo/odoo@acbca1195a3ad54fe5bc88ceae462993946335a6
        util.ensure_xmlid_match_record(cr, "point_of_sale.pos_sale_journal", "account.journal", {"code": "POSS"})
    if util.version_between("17.0", "18.0"):
        cr.execute(
            """
            WITH copy_payment_method AS (
                -- methods in use come first in the list
                SELECT array_agg((p_rel IS NULL, ppm.id) ORDER BY p_rel IS NULL, ppm.id) AS to_remove
                  FROM pos_payment_method ppm
                  JOIN account_journal aj
                    ON aj.id = ppm.journal_id
             LEFT JOIN pos_config_pos_payment_method_rel p_rel
                    ON p_rel.pos_payment_method_id = ppm.id
                 WHERE aj.type = 'cash'
                 GROUP BY ppm.journal_id
            )
            UPDATE pos_payment_method ppm
               SET active = FALSE
              FROM copy_payment_method cpm
                -- skip at least one pos payment, skip all that are used
             WHERE (True, ppm.id) = ANY(cpm.to_remove[2:])
         RETURNING ppm.id, name->>'en_US'
          """
        )
        if cr.rowcount:
            util.add_to_migration_reports(
                category="POS Payments",
                message=(
                    """
                    <details>
                        <summary>
                            During the upgrade, we found multiple records of POS payment methods
                            with the journal type "cash" which is not valid. To ensure compatibility
                            with the standard flow, the following POS payment method records have been archived.
                        </summary>
                            <ul>{}</ul>
                    </details>
                    """.format(
                        " ".join(
                            "<li>{}</li> ".format(util.get_anchor_link_to_record("pos.payment.method", id, name))
                            for id, name in cr.fetchall()
                        )
                    )
                ),
                format="html",
            )
