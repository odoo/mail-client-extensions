from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~15.3"):
        cr.execute(
            """
            UPDATE res_partner
               SET email_normalized = LOWER(SUBSTRING(email, '([^ ,;<@]+@[^> ,;]+)'))
             WHERE id = %s
               AND email_normalized IS NULL
            """,
            [util.ref(cr, "base.partner_demo_portal")],
        )
