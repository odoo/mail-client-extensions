from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "customer_satisfaction")

    # clip helpdesk_target_closed to int4 upper limit (2^31 - 1), before converting it from float
    cr.execute(
        """
        UPDATE res_users
           SET helpdesk_target_closed = 2147483647
         WHERE helpdesk_target_closed > 2147483647
        """
    )
    cr.execute("ALTER TABLE res_users ALTER COLUMN helpdesk_target_closed TYPE int4")

    util.rename_field(cr, "helpdesk.sla.report.analysis", "sla_status_failed", "sla_status_fail")

    util.remove_field(cr, "helpdesk.sla.report.analysis", "sla_exceeded_days")
    if not util.version_gte("saas~15.4"):
        util.remove_field(cr, "helpdesk.sla.report.analysis", "sla_id")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_open_hours")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_failed")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_fold")
    util.remove_field(cr, "helpdesk.sla.status", "exceeded_days")

    util.create_column(cr, "helpdesk_sla_status", "exceeded_hours", "float8")
    util.create_column(cr, "helpdesk_ticket", "sla_reached", "boolean")
