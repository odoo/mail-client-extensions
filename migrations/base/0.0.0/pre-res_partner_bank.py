from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # In saas~11.3 a constraint for not null partner_id was added
    # but it was never enforced in a migration script
    # At the moment of writing the next major version is 16.0
    # This should then cover all DBs in the wild with this issue
    if not util.version_between("saas~11.3", "16.0"):
        return
    cr.execute(
        """
        WITH new_partners AS (
           INSERT
             INTO res_partner(name, active, color)
           SELECT 'Partner for bank account ' || b.acc_number,
                  false,
                  b.id
             FROM res_partner_bank b
            WHERE b.partner_id IS NULL
        RETURNING id,
                  color AS bank_id
        )  UPDATE res_partner_bank b
              SET partner_id = new_partners.id
             FROM new_partners
            WHERE new_partners.bank_id = b.id
        RETURNING b.id
        """
    )
    if not cr.rowcount:
        return
    bids = cr.fetchall()
    cr.execute(
        """
        UPDATE res_partner p
           SET color = NULL
          FROM res_partner_bank b
         WHERE b.partner_id = p.id
           AND b.id IN %s
        """,
        [tuple(_id for _id, in bids)],
    )
