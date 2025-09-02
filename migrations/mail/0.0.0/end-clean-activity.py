from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "mail_activity"):
        _clean_activities(cr)


def _clean_activities(cr):
    env = util.env(cr)
    cr.execute("SELECT res_model FROM mail_activity GROUP BY res_model")
    for (model,) in cr.fetchall():
        if model not in env or not env[model]._auto:
            continue
        table = util.table_of_model(cr, model)
        if not util.table_exists(cr, table):
            continue
        util.explode_execute(
            cr,
            cr.mogrify(
                util.format_query(
                    cr,
                    """
                    DELETE
                      FROM mail_activity
                     USING mail_activity ma
                 LEFT JOIN {table} t
                        ON ma.res_id = t.id
                     WHERE mail_activity.id = ma.id
                       AND ma.res_model = %s
                       AND ma.res_id IS NOT NULL
                       AND t.id IS NULL
                    """,
                    table=table,
                ),
                [model],
            ).decode(),
            table="mail_activity",
            alias="ma",
        )
