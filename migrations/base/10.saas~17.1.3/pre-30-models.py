# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_model(cr, "res.font")
    util.delete_model(cr, "base.module.configuration")

    util.remove_field(cr, "ir.actions.todo", "type")
    util.remove_field(cr, "ir.actions.todo", "note")
    util.remove_field(cr, "ir.actions.todo", "groups_id")

    util.rename_field(cr, "res.company", "rml_header1", "report_header")
    util.rename_field(cr, "res.company", "rml_footer", "report_footer")

    for field in "rml_header rml_header2 rml_header3 font fax rml_paper_format".split():
        util.remove_field(cr, "res.company", field)

    util.create_column(cr, "res_country", "name_position", "varchar")
    cr.execute("UPDATE res_country SET name_position='before'")
    cr.execute("UPDATE res_country SET name_position='after' WHERE id=%s", [util.ref(cr, "base.jp")])

    cr.execute("SELECT sum((TRIM(COALESCE(fax, '')) != '')::integer) / count(*)::float > 0.05 FROM res_partner;")
    if cr.fetchone()[0] or os.environ.get("ODOO_MIG_FORCEFULLY_KEEP_FAX"):
        column_name = util.find_new_table_column_name(cr, "res_partner", "x_fax")
        cr.execute(
            """
            UPDATE ir_model_fields
               SET related = %s
             WHERE model = 'res.users' AND name = 'fax'
        """,
            ["partner_id." + column_name],
        )

        for model in ["res.partner", "res.users"]:
            util.rename_field(cr, model, "fax", column_name)
            util.move_field_to_module(cr, model, column_name, "base", "__upgrade__")
            cr.execute(
                """
                UPDATE ir_model_fields
                   SET state = 'manual'
                 WHERE model = %s AND name = %s
             """,
                (model, column_name),
            )
        try:
            util.add_view(
                cr,
                "res.partner.form.tax.upgrade",
                "res.partner",
                "form",
                """
            <data>
              <field name="mobile" position="after">
                <field name="%s"/>
              </field>
            </data>
            """
                % column_name,
                inherit_xml_id="base.view_partner_form",
            )
        except ValueError:
            util.add_to_migration_reports(
                """
                The fax field has been removed from the contact form in Odoo 11.0.
                Nevertheless, we detected you were using it
                and we therefore automatically preserved your data in a custom field "%s".
                Unfortunately, we were not able to add this field automatically in your contact form view,
                so you might want to add it manually yourself.
            """
                % column_name,
                "Removed fields",
            )
    else:
        util.remove_field(cr, "res.partner", "fax")
        util.remove_field(cr, "res.users", "fax")

    # ir.values,value text -> binary
    cr.execute("SELECT character_set_name FROM information_schema.character_sets")
    (charset,) = cr.fetchone()
    cr.execute(
        """
         ALTER TABLE ir_values ALTER COLUMN "value" TYPE bytea USING convert_to("value", '{0}')
    """.format(
            charset
        )
    )
    delattr(util.helpers._ir_values_value, "result")
