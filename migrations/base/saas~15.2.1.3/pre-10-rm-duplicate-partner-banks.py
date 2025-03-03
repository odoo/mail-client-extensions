# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    """This function removes res_partner_bank records that have duplicate pairings of
    sanitized_acc_number, partner_id such that only one record remains, in order to
    meet the new constraint in base/res_partner_bank.

    The constraint being added is unique(sanitized_acc_number, partner_id), and it
    is replacing the existing unique(sanitized_acc_number, company_id) constraint.
    In order to ensure the constraint is applied successfully, we need to reduce
    duplicate records to a single record.
    """
    cr.execute(
        """
        SELECT min(id) as id, (array_agg(id ORDER BY id))[2:] as others, bool_or(active)
          FROM res_partner_bank
      GROUP BY sanitized_acc_number, partner_id
        HAVING count(id) > 1
        """
    )

    # Res partner banks to be deleted
    dupes = cr.fetchall()

    # Replace references to the duplicate partner banks
    if not dupes:
        return
    util.remove_constraint(cr, "mail_followers", "mail_followers_mail_followers_res_partner_res_model_id_uniq")
    idmap = {o: id for id, others, _ in dupes for o in others}
    util.replace_record_references_batch(cr, idmap, "res.partner.bank")
    if util.table_exists(cr, "mail_followers"):
        cr.execute(
            """
            WITH duplicates AS (
                SELECT unnest((array_agg(id))[2:]) as id
                  FROM mail_followers
                 WHERE res_model = 'res.partner.bank'
              GROUP BY res_model, res_id, partner_id
                HAVING count(id) > 1
            )
            DELETE FROM mail_followers f
                  USING duplicates d
                  WHERE f.id = d.id
            """
        )
        cr.execute(
            """
            ALTER TABLE mail_followers
         ADD CONSTRAINT mail_followers_mail_followers_res_partner_res_model_id_uniq
                 UNIQUE (res_model, res_id, partner_id)
            """
        )

    # Remove the records
    util.remove_records(cr, "res.partner.bank", idmap.keys())

    # force deduplicated records to be active
    actives = set(id for id, _, active in dupes if active)
    if actives:
        cr.execute("UPDATE res_partner_bank SET active = true WHERE id IN %s AND active IS NOT true", [tuple(actives)])

    # Remove the current constraint before recomputing the company id
    util.remove_constraint(cr, "res_partner_bank", "res_partner_bank_unique_number")

    # recompute the `company_id`.
    cr.execute(
        """
        UPDATE res_partner_bank b
           SET company_id = p.company_id
          FROM res_partner p
         WHERE p.id = b.partner_id
        """
    )
