import psycopg2

from odoo.tools.misc import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #Rules without struct_id are not last level Rules, then can be deleted
    cr.execute("""
        SELECT imd.module,imd.name
        FROM hr_salary_rule r
        JOIN ir_model_data imd ON r.id = imd.res_id
                                  AND imd.model = 'hr.salary.rule'
   LEFT JOIN hr_payslip_line p ON p.salary_rule_id=r.id
        WHERE r.struct_id IS NULL
          AND imd.module in ('hr_payroll', 'l10n_be_hr_payroll')
          AND p.id IS NULL
    """)
    for name in cr.fetchall():
        util.remove_record(cr, name[0] + '.' + name[1])
    with ignore(psycopg2.Error), util.savepoint(cr):
        cr.execute("ALTER TABLE hr_salary_rule ALTER COLUMN struct_id SET NOT NULL")

    env = util.env(cr)

    if hasattr(env.registry, "_notnull_errors"):
        # Avoid the warning "unable to set constraint NOT NULL" raised by the ORM for Odoo <= saas~12.3
        # Rules without `struct_id` are deleted just above
        env.registry._notnull_errors.pop(("hr_salary_rule", "struct_id"), None)
        # Structure without `type_id` are assigned to a default type in hr_payroll/saas~12.3.1.0/post-migrate.py
        env.registry._notnull_errors.pop(("hr_payroll_structure", "type_id"), None)

    loaded_xmlids = env['ir.model'].pool.loaded_xmlids
    hsr_xmlids = env['ir.model.data'].search([('model', '=', 'hr.salary.rule')])

    for rule in hsr_xmlids:
        xmlid = '%s.%s' % (rule.module, rule.name)
        if xmlid not in loaded_xmlids:
            cr.execute("""
                SELECT count(*) FROM hr_payslip_line WHERE salary_rule_id = %s
            """ % rule.res_id)
            cnt = cr.fetchone()[0]
            if cnt > 0:
                env['hr.salary.rule'].browse(rule.res_id).active = False
                util.force_noupdate(cr, xmlid)

    # payslip lines now use salary_rule_id, before they actually **inherited** from salary rules
    util.remove_column(cr, "hr_payslip_line", "appears_on_payslip")
    util.remove_column(cr, "hr_payslip_line", "amount_select")
    util.remove_column(cr, "hr_payslip_line", "amount_fix")
    util.remove_column(cr, "hr_payslip_line", "amount_percentage")
