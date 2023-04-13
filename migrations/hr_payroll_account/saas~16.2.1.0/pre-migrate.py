from odoo.upgrade import util


def migrate(cr, version):
    xmlid = "hr_payroll_account.hr_payroll_account_journal"
    jid = util.ref(cr, xmlid)
    if jid and not util.delete_unused(cr, xmlid):
        cr.execute("SELECT company_id FROM account_journal WHERE id=%s", [jid])
        cid = cr.fetchone()[0]
        util.rename_xmlid(cr, xmlid, f"account.{cid}_hr_payroll_account_journal")
    cr.execute(
        """
           WITH t AS (
               SELECT SPLIT_PART(value_reference, ',' ,2)::integer AS journal_id,
                      company_id
                 FROM ir_property p
                 JOIN ir_model_fields f
                   ON f.id = p.fields_id
                WHERE f.model = 'hr.payroll.structure'
                  AND f.name = 'journal_id'
                  AND p.res_id LIKE 'hr.payroll.structure,%'
               GROUP BY 1, 2
           )
           INSERT INTO ir_model_data (model, res_id, module, name, noupdate)
                SELECT 'account.journal', acj.id,
                       'account', CONCAT(acj.company_id, '_hr_payroll_account_journal'), true
                  FROM t
                  JOIN account_journal acj
                    ON acj.id = t.journal_id
           ON CONFLICT DO NOTHING
        """
    )
