import logging

from psycopg2.extras import Json

from odoo.modules.module import get_modules

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase

_logger = logging.getLogger("odoo.upgrade.base.tests.test_rem")


def _model_tables(test):
    return Json({model_name: model._table for model_name, model in test.env.items()})


NON_STORED_FIELDS_EXCEPTIONS = {
    ("res.partner", "signup_token")  # computed with a phantom column hack
}


class TestStoredFields(UpgradeCase):
    query = """
        SELECT f.model,
               f.name
          FROM ir_model_fields f
          JOIN pg_class t
            ON t.relname = %s::jsonb->>f.model
          JOIN pg_attribute a
            ON t.oid = a.attrelid
           AND a.attname = f.name
           AND NOT a.attisdropped
           AND pg_catalog.format_type(a.atttypid, a.atttypmod) NOT IN ('cid', 'tid', 'oid', 'xid')
          JOIN ir_model_data d
            ON d.res_id = f.id
           AND d.model = 'ir.model.fields'
         WHERE f.store {}
           AND d.module IN %s
         GROUP BY f.id
    """

    def check(self, value):
        value = set(map(tuple, value)) - NON_STORED_FIELDS_EXCEPTIONS
        self.env.cr.execute(self.query.format("IS NOT True"), [_model_tables(self), tuple(get_modules())])
        wrong = [x for x in self.env.cr.fetchall() if x in value]
        self.assertFalse(wrong, "Some fields became non-stored and their columns still remain")

    def prepare(self):
        self.env.cr.execute(self.query.format(""), [_model_tables(self), tuple(get_modules())])
        return self.env.cr.fetchall()


class TestConstraints(UpgradeCase):
    def check(self, value):
        self.env.cr.execute(
            """
            SELECT m.id,
                   tc.conname,
                   m.model
              FROM ir_model m
              JOIN pg_class t
                ON t.relname = %s::jsonb->>m.model
              JOIN pg_constraint tc
                ON tc.conrelid = t.oid
               AND tc.contype IN ('c', 'u', 'x')
         LEFT JOIN ir_model_constraint mc
                ON left(mc.name, 63) = tc.conname
               AND mc.model = m.id
             WHERE mc IS NULL
             ORDER BY m.id, tc.conname
            """,
            [_model_tables(self)],
        )
        value = set(map(tuple, value))
        wrong = [(mname, cname) for mid, cname, mname in self.env.cr.fetchall() if (mid, cname) in value]
        self.assertFalse(wrong, "Some removed constraints still remain as table constraints")

    def prepare(self):
        self.env.cr.execute(
            """
            SELECT mc.model,
                   mc.name
              FROM ir_model_constraint mc
              JOIN ir_model m
                ON mc.model = m.id
              JOIN pg_class t
                ON t.relname = %s::jsonb->>m.model
              JOIN pg_constraint tc
                ON tc.conrelid = t.oid
               AND tc.conname = left(mc.name, 63)
               AND tc.contype IN ('c', 'u', 'x')
              JOIN ir_model_data d
                ON d.res_id = mc.id
               AND d.model = 'ir.model.constraint'
             WHERE mc.type != 'f'
               AND d.module IN %s
             GROUP BY mc.id
            """,
            [_model_tables(self), tuple(get_modules())],
        )
        return self.env.cr.fetchall()
