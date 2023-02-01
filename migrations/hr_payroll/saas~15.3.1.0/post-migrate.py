# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            WITH new_notes AS (
                INSERT INTO note_note(company_id, name, user_id, sequence, create_uid, create_date)
                     SELECT id, 'Payroll Note', 1, 10, 1, now() at time zone 'UTC'  FROM res_company
                  RETURNING id, company_id
            ), tags AS (
                INSERT INTO note_tags_rel(note_id, tag_id)
                     SELECT id, %s FROM new_notes
            )
            INSERT INTO mail_followers(res_model, res_id, partner_id)
                 SELECT 'note.note', n.id, ru.partner_id
                   FROM new_notes n
                   JOIN res_company_users_rel rc ON rc.cid = n.company_id
                   JOIN res_users ru ON ru.id = rc.user_id
                   JOIN res_groups_users_rel rg ON rg.uid = ru.id
                  WHERE rg.gid = %s
            ON CONFLICT DO NOTHING
        """,
        [util.ref(cr, "hr_payroll.payroll_note_tag"), util.ref(cr, "hr_payroll.group_hr_payroll_user")],
    )
