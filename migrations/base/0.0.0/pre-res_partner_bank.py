from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # In saas~11.3 a constraint for not null partner_id was added
    # but it was never enforced in a migration script
    # At the moment of writing the next major version is 16.0
    # This should then cover all DBs in the wild with this issue
    if util.version_between("saas~11.3", "16.0"):
        _no_bank_without_partner(cr)


def _no_bank_without_partner(cr):
    cr.execute(
        """
        CREATE FUNCTION _upg_not_null_partner() RETURNS TABLE(id int)
        AS $$
            BEGIN
                RETURN QUERY WITH new_partners AS (
                   INSERT
                     INTO res_partner(name, active, color)
                   SELECT 'Partner for bank account ' || b.acc_number,
                          false,
                          b.id
                     FROM res_partner_bank b
                    WHERE b.partner_id IS NULL
                RETURNING res_partner.id,
                          res_partner.color AS bank_id
                )  UPDATE res_partner_bank b
                      SET partner_id = new_partners.id
                     FROM new_partners
                    WHERE new_partners.bank_id = b.id
                RETURNING b.partner_id;
                RETURN;
            EXCEPTION
                WHEN not_null_violation THEN RETURN;
            END;
        $$
        LANGUAGE PLPGSQL
        """
    )
    cr.execute("SELECT * FROM _upg_not_null_partner()")
    if cr.rowcount:
        cr.execute(
            """
            UPDATE res_partner p
               SET color = NULL
             WHERE p.id IN %s
            """,
            [tuple(_id for (_id,) in cr.fetchall())],
        )
    cr.execute("DROP FUNCTION _upg_not_null_partner()")
