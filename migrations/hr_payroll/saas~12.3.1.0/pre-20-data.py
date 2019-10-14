# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_payroll.{benefit,work_entry}_type_leave_form_inherit"))
    util.rename_xmlid(cr, *eb("hr_payroll.{report_contribution,contribution_}register"))

    # Main idea is to flatten the structures (which is hierarchical)
    # And convert the M2M (from structure to rules) to a O2M (by duplicating rules)

    base_struct = util.ref(cr, "hr_payroll.structure_base")
    if base_struct:
        cr.execute("SELECT count(1) FROM hr_payslip WHERE struct_id = %s", [base_struct])
        if not cr.fetchone()[0]:
            # structure not used, we can remove it safely
            util.remove_record(cr, "hr_payroll.structure_base")
        else:
            util.force_noupdate(cr, "hr_payroll.structure_base", True)

    cr.execute("""
        UPDATE hr_salary_rule
           SET appears_on_payslip=FALSE
         WHERE parent_rule_id IS NOT NULL
    """)

    # Set struct_id on last level rules
    cr.execute("""
        WITH upd AS (
            SELECT struct_id, rule_id
              FROM hr_structure_salary_rule_rel r
             WHERE NOT EXISTS ( SELECT 1
                                  FROM hr_payroll_structure
                                 WHERE parent_id=r.struct_id
                              )
        )
        UPDATE hr_salary_rule r
           SET struct_id=upd.struct_id
          FROM upd
         WHERE r.id=upd.rule_id
    """)

    # Flatten structures by duplicating rules coming from parents ( max 2 parents level )
    cr.execute("""
    INSERT INTO hr_salary_rule(struct_id, name, code, sequence, quantity, category_id, active, appears_on_payslip, condition_select, condition_range, condition_python, condition_range_min, condition_range_max, amount_select, amount_fix, amount_percentage, amount_python_compute, amount_percentage_base, partner_id, note)
        SELECT p1.id as struct_id,
               r.name, r.code, r.sequence, r.quantity, r.category_id, r.active, r.appears_on_payslip, r.condition_select, r.condition_range, r.condition_python, r.condition_range_min, r.condition_range_max, r.amount_select, r.amount_fix, r.amount_percentage, r.amount_python_compute, r.amount_percentage_base, r.partner_id, r.note
          FROM hr_payroll_structure p1
     LEFT JOIN hr_payroll_structure p2 ON p1.parent_id=p2.id
     LEFT JOIN hr_payroll_structure p3 ON p2.parent_id=p3.id

    INNER JOIN hr_structure_salary_rule_rel rel ON (p2.id=rel.struct_id OR p3.id=rel.struct_id)
    INNER JOIN hr_salary_rule r on rel.rule_id=r.id

         WHERE p1.id NOT IN (SELECT parent_id FROM hr_payroll_structure)
    """)

    #Rules without struct_id are not last level Rules, then can be deleted
    cr.execute("""
        SELECT imd.name
        FROM hr_salary_rule r
        JOIN ir_model_data imd ON r.id = imd.res_id
                                  AND imd.model = 'hr.salary.rule'
        WHERE r.struct_id IS NULL
    """)
    for name in cr.fetchall():
        util.delete_unused(cr, 'hr_payslip_line' , ['hr_salary_rule.' + name[0]])
