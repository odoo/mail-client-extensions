# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def move_field(cr, model, field, coltype, default):
    util.move_field_to_module(cr, model, field, "website_forum", "gamification")
    table = util.table_of_model(cr, model)
    util.create_column(cr, table, field, coltype)
    if default is not None:
        cr.execute("UPDATE {0} SET {1} = %s WHERE {1} IS NULL".format(table, field), [default])

def migrate(cr, version):
    util.remove_record(cr, 'gamification.mt_badge_granted')

    move_field(cr, "gamification.badge", "level", "varchar", "bronze")
    move_field(cr, "gamification.badge.user", "level", "varchar", "bronze")

    for field in {"badge_ids", "gold_badge", "silver_badge", "bronze_badge"}:
        util.move_field_to_module(cr, "res.users", field, "website_forum", "gamification")

    if util.column_exists(cr, "res_users", "karma"):
        # we need to have the `karma` column to be zeroed for all users to
        # avoid *each* `gamification.karma.rank` creation to spam users.
        # Rank will be recomputed in `end-` script.
        cr.execute("ALTER TABLE res_users RENAME COLUMN karma TO _karma")
    # default value is required to avoid `[('karma', '>', 0)]` domain to return all users...
    util.move_field_to_module(cr, "res.users", "karma", "website_forum", "gamification")
    cr.execute("ALTER TABLE res_users ADD COLUMN karma int4 DEFAULT 0")
