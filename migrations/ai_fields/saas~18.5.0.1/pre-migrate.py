import ast
import re

import lxml.html
from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype = 'properties_definition'
           AND store = TRUE
        """,
    )
    for model, field_name in cr.fetchall():
        table = util.table_of_model(cr, model)

        # Early filter in SQL, then migrate the `ai_prompt` in python
        # only on the records matching the condition

        cr.execute(
            util.format_query(
                cr,
                """
                    SELECT id, {field_name} AS properties
                      FROM {table}
                     WHERE {field_name}::text LIKE ANY(ARRAY['%o\\_ai\\_field%', '%o\\_ai\\_record%'])
                """,
                table=util.table_of_model(cr, model),
                field_name=field_name,
            ),
        )

        for lid, properties in cr.fetchall():
            updated = False
            for definition in properties:
                ai_prompt = definition.get("system_prompt") or ""
                if "o_ai_field" in ai_prompt or "o_ai_record" in ai_prompt:
                    definition["system_prompt"] = migrate_ai_prompt(ai_prompt)
                    updated = True
            if not updated:
                continue

            cr.execute(
                util.format_query(
                    cr,
                    "UPDATE {table} SET {field_name} = %s WHERE id = %s",
                    table=table,
                    field_name=field_name,
                ),
                [Json(properties), lid],
            )

    cr.execute(
        """
        SELECT id, system_prompt
          FROM ir_model_fields
         WHERE system_prompt IS NOT NULL
           AND (system_prompt LIKE '%o_ai_field%' OR system_prompt LIKE '%o_ai_record%')
           AND store = TRUE
        """,
    )
    for line in cr.dictfetchall():
        cr.execute(
            "UPDATE ir_model_fields SET system_prompt = %s WHERE id = %s",
            (migrate_ai_prompt(line["system_prompt"]), line["id"]),
        )


def migrate_ai_prompt(prompt):
    root = lxml.html.fromstring(prompt)

    # Only the `t-out` was checked, not `data-ai-field` so for the migration,
    # we only trust the `t-out` attribute and we remove all existing `data-ai-field`
    for el in root.xpath("//*[@data-ai-field]"):
        el.attrib.pop("data-ai-field")

    # Migrate inserted fields to `<span data-ai-field="partner_id.name">Partner > Name</span>`
    for el in root.xpath("//t"):
        # Now `data-ai-field` is only on a `<span/>` (and we will do normal sanitization)
        el.tag = "span"

    for el in root.xpath("//*[@t-out]"):
        field_chain = el.attrib.pop("t-out")
        field_chain = field_chain.removesuffix("._ai_format_mail_messages()")

        if re.fullmatch(r"[a-z_.]+", field_chain):
            # When we didn't call `ai_read`, the field chain was simply in `t-out`
            el.attrib["data-ai-field"] = field_chain.split("object.", 1)[-1]
            continue

        if field_chain.startswith("object._ai_read"):
            # AI read the field
            field_list = field_chain[len("object._ai_read") :]
            try:
                field_list = ast.literal_eval(field_list)
            except Exception:
                field_list = ()

            # Remove all child and rebuild the XML
            for child_el in el:
                child_el.drop_tree()

            # Re-add the child from the field we read with `object._ai_read`
            for field in field_list:
                child_el = lxml.html.Element("span")
                child_el.attrib["data-ai-field"] = field
                el.append(child_el)

    for el in root.xpath("//*[@t-out]"):
        el.attrib.pop("t-out")

    for el in root.xpath("//*[@data-ai-field]"):
        el.attrib.pop("class", None)
        el.attrib["data-oe-protected"] = "true"

    # Default records are now added server side
    for el in root.xpath("//*[contains(@class, 'o_ai_default_record')]"):
        el.drop_tree()

    # Migrate inserted record to `<span data-ai-record="99"/>`
    for el in root.xpath("//*[contains(@class, 'o_ai_record')]"):
        m = re.search(r"{\s*([0-9]+)\s*:.*?}", lxml.html.tostring(el).decode())
        if m:
            el.attrib["data-ai-record-id"] = m.group(1)
        el.attrib.pop("class", None)
        el.tag = "span"

    for el in root.xpath("//*[@data-ai-record-id]/*"):
        el.drop_tree()

    for el in root.xpath("//*[contains(@class, 'd-none')]"):
        el.drop_tree()

    return lxml.html.tostring(root, method="xml").decode()
