"""
Complement of `pre-resequence-custom-report-line.py`
"""

from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def order_siblings(lines, custom_lines, pre_upg_rank):
    """
    Assume standard lines are already in the right (relative) order.
    Insert custom lines right after the closest preceding line according to the pre-upgrade ranking.
    """
    lines_sorted = [line for line in lines if line.id not in custom_lines]
    lines_by_pre_upg_rank = sorted(
        lines,
        key=lambda line: pre_upg_rank.get(line.id, float("inf")),  # new lines last
    )

    insert_idx = 0
    for line in lines_by_pre_upg_rank:
        if line.id in custom_lines:
            lines_sorted.insert(insert_idx, line)
            insert_idx += 1
        else:
            insert_idx = lines_sorted.index(line) + 1

    return lines_sorted


def sort_report_tree(root_lines, custom_lines, pre_upg_rank):
    for line in order_siblings(root_lines, custom_lines, pre_upg_rank):
        yield line
        for child in sort_report_tree(line.children_ids, custom_lines, pre_upg_rank):
            yield child


def resequence_lines(cr):
    std_modules = tuple(modules.get_modules() + ["test_upg"])  # for testing purposes
    cr.execute(
        """
        SELECT line.id
          FROM account_report_line line
     LEFT JOIN ir_model_data imd_line
            ON imd_line.res_id = line.id
           AND imd_line.model = 'account.report.line'
           AND imd_line.module IN %s
          JOIN ___std_reports_with_custom_lines report
            ON report.id = line.report_id
         WHERE imd_line IS NULL
        """,
        [std_modules],
    )
    custom_lines = {id_ for (id_,) in cr.fetchall()}

    cr.execute("SELECT id, rank FROM ___pre_upg_arl_order_info")
    pre_upg_rank = dict(cr.fetchall())

    arl = util.env(cr)["account.report.line"]
    cr.execute("SELECT id FROM ___std_reports_with_custom_lines")
    for (report_id,) in cr.fetchall():
        root_lines = arl.search([("report_id", "=", report_id), ("parent_id", "=", False)])
        new_order = [line.id for line in sort_report_tree(root_lines, custom_lines, pre_upg_rank)]
        cr.execute(
            """
            UPDATE account_report_line
               SET sequence = ARRAY_POSITION(%s, id) * 10
             WHERE id = ANY(%s)
         RETURNING id, sequence
            """,
            [new_order, new_order],
        )


def migrate(cr, version):
    if util.version_gte("17.0"):  # account.report.line was introduced in Odoo 16
        cr.execute("SELECT 1 FROM ___pre_upg_arl_order_info")
        if cr.rowcount:
            resequence_lines(cr)

        cr.execute("DROP TABLE ___pre_upg_arl_order_info")
        cr.execute("DROP VIEW ___std_reports_with_custom_lines")
