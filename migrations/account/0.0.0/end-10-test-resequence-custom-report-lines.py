"""
Simulate standard lines being removed, created and moved by the ORM, as needed by `TestResequenceCustomLines`
"""

from odoo.addons.base.maintenance.migrations import util


def remove_line(cr, xmlid):
    assert "." in xmlid, "xmlid should follow the <module>.<name> format"
    module, _, name = xmlid.partition(".")

    cr.execute(
        """
        WITH removed_imd AS (
            DELETE
              FROM ir_model_data
             WHERE module = %s
               AND name = %s
         RETURNING res_id
        )
        DELETE
          FROM account_report_line l
         USING removed_imd ld
         WHERE ld.res_id = l.id
        """,
        [module, name],
    )


def create_line(cr, xmlid, vals):
    assert "." in xmlid, "xmlid should follow the <module>.<name> format"
    module, _, name = xmlid.partition(".")

    cr.execute(
        """
        WITH new_line AS (
            INSERT INTO account_report_line (name, hierarchy_level, parent_id, report_id)
            VALUES (JSONB_BUILD_OBJECT('en_US', %s), %s, %s, %s)
         RETURNING id, name->>'en_US' AS name
        )
        INSERT INTO ir_model_data (module, name, model, res_id)
        SELECT %s, %s, 'account.report.line', id
          FROM new_line
        """,
        [
            vals["name"],
            vals["hierarchy_level"],
            vals["parent_id"],
            vals["report_id"],
            module,
            name,
        ],
    )


def migrate(cr, version):
    if util.version_gte("17.0") and util.table_exists(cr, "upgrade_test_data"):
        _fix_test_data(cr)


def _fix_test_data(cr):
    cr.execute(
        "SELECT value FROM upgrade_test_data WHERE key = 'account.tests.test_account_custom_report_lines.TestResequencedCustomLines'"
    )
    if not cr.rowcount:
        return

    post_upg_expected_lines_order = cr.fetchone()[0]

    report_xmlid_template = "test_upg.upg_test_account_report_{}"
    line_xmlid_template = "test_upg.upg_test_account_report_line_{}_{}"

    # Report 1
    create_line(
        cr,
        line_xmlid_template.format("std_z", "r1"),
        {
            "name": "std_z",
            "hierarchy_level": 1,
            "parent_id": None,
            "report_id": util.ref(cr, report_xmlid_template.format("r1")),
        },
    )

    # Report 3
    remove_line(cr, line_xmlid_template.format("std_a", "r3"))

    # Report 4
    remove_line(cr, line_xmlid_template.format("std_b", "r4"))
    remove_line(cr, line_xmlid_template.format("std_b_1", "r4"))

    # Report 5
    remove_line(cr, line_xmlid_template.format("std_b_1", "r5"))

    # Report 6
    remove_line(cr, line_xmlid_template.format("std_c", "r6"))
    cr.execute(
        """
        UPDATE account_report_line
           SET parent_id = %s
         WHERE id = %s
        """,
        [
            util.ref(cr, line_xmlid_template.format("std_a", "r6")),
            util.ref(cr, line_xmlid_template.format("std_c_1", "r6")),
        ],
    )

    # mock resequencing of standard lines for test reports
    ar = util.env(cr)["account.report"]
    for report_id, line_names in post_upg_expected_lines_order.items():
        report_id = int(report_id)  # noqa: PLW2901
        std_lines = [
            util.ref(cr, line_xmlid_template.format(line_name, ar.browse(report_id).name))
            for line_name in line_names
            if line_name.startswith("std_")
        ]

        cr.execute(
            """
            UPDATE account_report_line
               SET sequence = ARRAY_POSITION(%s, id) * 10
             WHERE report_id = %s
               AND id = ANY(%s)
            """,
            [std_lines, report_id, std_lines],
        )
