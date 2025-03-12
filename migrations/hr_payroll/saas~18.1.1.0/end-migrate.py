from collections import defaultdict

from odoo import modules

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT hsr.id, hsr.name->>'en_US',
               hsr.category_id AS cid,
               cat.name->>'en_US' AS cname
          FROM hr_salary_rule hsr
          JOIN hr_payroll_structure st
            ON hsr.struct_id = st.id
          JOIN hr_salary_rule_category cat
            ON cat.id = hsr.category_id
          JOIN ir_model_data d
            ON d.model = 'hr.salary.rule.category'
           AND d.res_id = cat.id
         WHERE st.country_id != cat.country_id
           AND d.module IN %s
        """,
        [tuple(modules.get_modules())],
    )
    if cr.rowcount:
        grouped = defaultdict(list)
        for rid, rname, cid, cname in cr.fetchall():
            grouped[(cid, cname)].append((rid, rname))
        util.add_to_migration_reports(
            category="Salary Rule Categories",
            format="html",
            message=(
                """
                <details>
                    <summary>
                        A new field, <b>Country</b>, and a constraint have been added to <b>Salary Rule Categories</b>
                        to ensure that a <b>Salary Rule's Category</b> matches the <b>Salary Structure's Country</b>.
                        There are conflicting countries in rules vs categories as listed below.
                        Please review them and, if necessary, update the records in your database,
                    </summary>
                    <ul>
                        {}
                    </ul>
                </details>
                """.format(
                    "\n".join(
                        f"""<li>
                                category: {util.get_anchor_link_to_record("hr.salary.rule.category", cid, cname)}
                                <ul>
                                    {"".join(f"<li>rule: {util.get_anchor_link_to_record('hr.salary.rule', rid, rname)}</li>" for rid, rname in rules)}
                                </ul>
                            </li>"""
                        for (cid, cname), rules in grouped.items()
                    ),
                )
            ),
        )
