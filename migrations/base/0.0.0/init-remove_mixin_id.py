import logging

_logger = logging.getLogger(__name__)


def prepare_migration(cr):
    cr.execute("SELECT latest_version FROM ir_module_module WHERE name='base'")
    version = cr.fetchone()[0]
    version = tuple(map(int, version.replace("saas~", "").split(".")[:2]))
    if (15, 0) <= version <= (18, 0):
        cr.execute(
            """
            WITH rem_field AS (
                DELETE FROM ir_model_fields
                      WHERE name = 'id'
                        AND model IN ('studio.mixin', 'mail.alias.mixin')
                  RETURNING id, model
            ), rem_imd AS (
                DELETE FROM ir_model_data d
                      USING rem_field
                      WHERE d.res_id = rem_field.id
                        AND d.model = 'ir.model.fields'
            ) SELECT model FROM rem_field
            """
        )
        if cr.rowcount:
            _logger.warning("Dangling mixin id field removed from: %s", [model for (model,) in cr.fetchall()])
