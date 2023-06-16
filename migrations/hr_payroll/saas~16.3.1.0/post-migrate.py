# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    note_tag = util.ref(cr, "hr_payroll.payroll_note_tag")
    if not note_tag:
        return

    cr.execute(
        """
        INSERT INTO hr_payroll_note(company_id, name, note, create_uid, write_uid, create_date, write_date)
        SELECT n.company_id, n.name, n.memo, n.create_uid, n.write_uid, n.create_date, n.write_date
          FROM note_note n
          JOIN note_tags_rel nt
            ON nt.note_id = n.id
         WHERE nt.tag_id = %s
           AND n.memo IS NOT NULL
    """,
        [note_tag],
    )
