from odoo.upgrade import util


def migrate(cr, version):
    note_tag = util.ref(cr, "hr_payroll.payroll_note_tag")
    if note_tag:
        cr.execute(
            """
            INSERT INTO hr_payroll_note(company_id, name, note, create_uid, write_uid, create_date, write_date)
                 SELECT c.id, COALESCE(n.name, 'Notes'), n.memo, n.create_uid, n.write_uid, n.create_date, n.write_date
                   FROM note_note n
                   JOIN note_tags_rel nt
                     ON nt.note_id = n.id
                   JOIN res_company c
                     ON n.company_id = c.id  -- Notes with company_id
                     OR n.company_id IS NULL -- Notes with null company_id are displayed by default for all companies
                  WHERE nt.tag_id = %s
                    AND n.memo IS NOT NULL
            """,
            [note_tag],
        )
