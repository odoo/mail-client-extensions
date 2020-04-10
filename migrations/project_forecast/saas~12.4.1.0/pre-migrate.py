# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~12.5"):
        model = "planning.slot"
        table = util.table_of_model(cr, model)
        util.drop_depending_views(cr, table, "start_datetime")
        util.drop_depending_views(cr, table, "end_datetime")

        field_name_mapping = [
            ("start_date", "start_datetime"),
            ("end_date", "end_datetime"),
        ]
        util.update_server_actions_fields(cr, src_model="planning.slot", fields_mapping=field_name_mapping)
    else:
        model = "project.forecast"
        table = util.table_of_model(cr, model)
        util.drop_depending_views(cr, table, "start_date")
        util.drop_depending_views(cr, table, "end_date")
        util.rename_field(cr, model, "start_date", "start_datetime")
        util.rename_field(cr, model, "end_date", "end_datetime")

    cr.execute("ALTER TABLE %s ALTER COLUMN start_datetime TYPE timestamp without time zone" % table)
    cr.execute(
        """
            ALTER TABLE %s
           ALTER COLUMN end_datetime
                   TYPE timestamp without time zone
                  USING end_datetime + interval '23:59:59'
        """
        % table
    )

    util.create_column(cr, table, "recurrency_id", "int4")
    util.create_column(cr, table, "published", "boolean")
    cr.execute("UPDATE %s SET published = false" % table)

    util.remove_field(cr, "res.company", "forecast_uom")
    util.remove_field(cr, "res.company", "forecast_span")
    util.remove_field(cr, "res.config.settings", "forecast_uom")
    util.remove_field(cr, "res.config.settings", "forecast_span")

    if util.version_gte("saas~12.5"):
        # Only make sense in saas~12.4
        return

    util.create_column(cr, "res_company", "forecast_default_view", "varchar")
