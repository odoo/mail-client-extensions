from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "res.config.installer")

    # this cron doesn't support interval_type='months'
    cron_id = util.ref(cr, "crm.ir_cron_crm_lead_assign")
    if cron_id:
        cr.execute(
            """
            UPDATE ir_cron
               SET active = false,
                   interval_type = 'weeks'
             WHERE interval_type IS NULL
               AND id = %s
            """,
            [cron_id],
        )

    cr.execute("""
        UPDATE ir_cron
           SET active = false,
               interval_type = 'months'
         WHERE interval_type IS NULL
    """)

    cr.execute("""
        UPDATE ir_cron
           SET active = false,
               interval_number = 1
         WHERE interval_number is NULL
    """)
