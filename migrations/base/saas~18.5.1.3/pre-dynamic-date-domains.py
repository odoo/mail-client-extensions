import html
import os.path
from importlib.machinery import SourceFileLoader

import odoo

from odoo.upgrade import util


def migrate(cr, version):
    for path in odoo.__path__:
        module_path = os.path.join(path, "upgrade_code/18.5-00-domain-dynamic-dates.py")
        if os.path.isfile(module_path):
            break
    else:
        raise OSError("Upgrade code not found for dynamic dates")
    module = SourceFileLoader("domain_dynamic_dates", module_path).load_module()
    transform = module.UpgradeDomainTransformer().transform
    NoChange = module.NoChange

    unchanged = []
    for domain_field in util.domains._get_domain_fields(cr):
        cr.execute(
            util.format_query(
                cr,
                """
                    SELECT {column}
                      FROM {table} t
                     WHERE {column} ~ 'context_today|datetime\\.'
                  GROUP BY {column}
                """,
                table=domain_field.table,
                column=domain_field.domain_column,
            )
        )
        for [domain] in util.log_progress(
            cr.fetchall(),
            util._logger,
            qualifier=f"{domain_field.table}.{domain_field.domain_column} rows",
            size=cr.rowcount,
        ):
            try:
                new_domain = transform(domain)
            except NoChange:
                unchanged.append((domain_field.table, domain))
            except Exception:
                util._logger.debug("Cannot transform domain %r", domain, exc_info=True)
            else:
                cr.execute(
                    util.format_query(
                        cr,
                        "UPDATE {table} SET {column} = %s WHERE {column} = %s",
                        table=domain_field.table,
                        column=domain_field.domain_column,
                    ),
                    [new_domain, domain],
                )

    if unchanged:
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        Some domains were not converted for dynamic dates.
                        You should rewrite domains containing <code>context_today</code> as values
                        with the new syntax for dynamic dates.
                        Check the <a href="https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#search-read">documentation</a>.
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(
                " ".join(
                    f"<li>Table: {html.escape(table)}, Domain: {html.escape(domain)}</li>"
                    for table, domain in unchanged
                )
            ),
            category="Base",
            format="html",
        )
