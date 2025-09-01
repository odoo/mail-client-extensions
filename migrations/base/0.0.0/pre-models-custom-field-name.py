import logging

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    _logger = logging.getLogger(__name__)

    # custom field names must start with a x_ and should not have spaces
    cr.execute(
        r"""
            SELECT model,
                   name
              FROM ir_model_fields
             WHERE state='manual'
               AND (name NOT LIKE 'x\_%' OR name LIKE '% %')
               AND name NOT IN (
                    '__last_update',
                    'create_date',
                    'create_uid',
                    'display_name',
                    'id',
                    'write_date',
                    'write_uid'
                   )
        """,
    )
    renamed = []
    for model, name in cr.fetchall():
        new_name = name.strip(" _").replace(" ", "_")
        if not new_name.startswith("x_"):
            new_name = "x_" + new_name
        util.rename_field(cr, model, name, new_name)
        renamed.append((name, new_name))
        _logger.info("ir_model_fields manual fields name: '%s' renamed field '%s' to '%s'", model, name, new_name)

    if renamed:
        li = "\n".join(
            "<li>{} &#8594; {}</li>".format(util.html_escape(name), util.html_escape(new_name))
            for name, new_name in renamed
        )
        util.add_to_migration_reports(
            """
                <details>
                <summary>
                    Custom field names must start with <kbd>x_</kbd> and may not
                    include spaces. The following fields were renamed:
                </summary>
                <ul>{}</ul>
                </details>
            """.format(li),
            "Custom Field Names",
            format="html",
        )
