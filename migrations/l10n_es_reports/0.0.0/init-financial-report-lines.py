# -*- coding: utf-8 -*-


def prepare_migration(cr):
    cr.execute(
        r"""
            SELECT REGEXP_REPLACE(latest_version, '\.\d+\.\d+$', '')
              FROM ir_module_module
             WHERE name = 'base'
        """
    )
    version = cr.fetchone()[0]

    if version in {"12.0", "saas~12.3", "13.0"}:
        cr.execute(
            """
                UPDATE ir_model_data
                   SET noupdate = true
                 WHERE module = 'l10n_es_reports'
                   AND name IN (
                       'mod_347_operations_regular_bought',
                       'mod_347_operations_regular_sold'
                   )
            """
        )
