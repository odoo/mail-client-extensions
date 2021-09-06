# -*- coding: utf-8 -*-
import logging

from openerp.release import version

from openerp.addons.base.maintenance.migrations import util

NS = "openerp.addons.base.maintenance.migrations.mail.{}.{}"
_logger = logging.getLogger(NS.format(version.rstrip(".0"), __name__))


def clean(cr, table, model_col="res_model", id_col="res_id"):
    cr.execute("SELECT {model_col} FROM {table} WHERE {model_col} IS NOT NULL GROUP BY {model_col}".format(**locals()))
    for (model,) in cr.fetchall():
        adj = ""
        target_table = util.table_of_model(cr, model)
        if util.table_exists(cr, target_table):
            query = """
              WITH orphans AS (
                SELECT t.id
                  FROM {table} t
             LEFT JOIN {target_table} g ON (t.{id_col} = g.id)
                 WHERE t.{model_col} = %s
                   AND g.id IS NULL
              )
              DELETE FROM {table} t
                    USING orphans o
                    WHERE o.id = t.id
            """
            cr.execute(query.format(**locals()), [model])

        else:
            adj = " unexisting"
            cr.execute("DELETE FROM {table} WHERE {model_col}=%s".format(**locals()), [model])

        deleted = cr.rowcount
        if deleted:
            _logger.info("DELETE %(deleted)d %(table)s unreachable rows for%(adj)s model %(model)s", locals())


def migrate(cr, version):
    clean(cr, "mail_followers")

    # Create missing index.
    # Without it, deletion is way loooonger!
    if not util.get_index_on(cr, "mail_mail", "mail_message_id"):
        cr.execute("CREATE INDEX mail_mail_mail_message_id_index ON mail_mail(mail_message_id)")

    parent_id_fk = next(
        (fk for fk in util.get_fk(cr, "mail_message") if fk[0] == "mail_message" and fk[1] == "parent_id"), None
    )
    if parent_id_fk:
        _, _, constraint, on_delete = parent_id_fk
        cr.execute("ALTER TABLE mail_message DROP CONSTRAINT %s" % constraint)

    clean(cr, "mail_message", "model")

    if parent_id_fk:
        _, _, constraint, on_delete = parent_id_fk
        on_delete = {
            "a": "NO ACTION",
            "c": "CASCADE",
            "r": "RESTRICT",
            "n": "SET NULL",
            "d": "SET DEFAULT",
        }.get(on_delete)

        # Clean the column in order to be able to reapply the constraint
        cte = """
            WITH bad_messages AS (
                SELECT m.id
                  FROM mail_message m
             LEFT JOIN mail_message p ON p.id = m.parent_id
            WHERE p.id IS NULL
              AND m.parent_id IS NOT NULL
            )
        """
        if on_delete == "CASCADE":
            cr.execute(cte + "DELETE FROM mail_message m USING bad_messages b WHERE m.id = b.id")
        else:
            # bad news if it was `RESTRICT`, the parent is gone; set it to NULL
            cr.execute(cte + "UPDATE mail_message m SET parent_id = NULL FROM bad_messages b WHERE b.id = m.id")

        cr.execute(
            """
                ALTER TABLE mail_message
                        ADD CONSTRAINT %s FOREIGN KEY (parent_id)
                            REFERENCES mail_message(id)
                            ON DELETE %s
            """
            % (constraint, on_delete)
        )


if __name__ == "__main__":
    env = env  # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
