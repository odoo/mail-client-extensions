# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from operator import itemgetter


def migrate(cr, version):
    """ Verify that there is no cycle between parent_tax and child_tax

        Also provide a beautiful display of the error that only show one line by issue.
        For instance [10,11,12,11] is the same issue as [23,4,12,11,12]
        because 11 reference 12 and 12 references 11 and so on ...
        So only show the cycle [11, 12, 11]
    """
    cr.execute(
        """WITH RECURSIVE cycle_(child_tax, parent_tax, depth_, path_, has_cycle) AS
        (
            SELECT child_tax, parent_tax, 0, ARRAY[child_tax], FALSE FROM account_tax_filiation_rel
            UNION
            SELECT cycle_.child_tax, r.parent_tax, depth_+1, path_||r.child_tax, r.child_tax=ANY(path_)
            FROM account_tax_filiation_rel r, cycle_
            WHERE r.child_tax = cycle_.parent_tax
            AND depth_ < 10
            AND has_cycle = false
        )
        SELECT path_ FROM cycle_
        WHERE has_cycle = true """
    )
    if cr.rowcount:
        filtered_cycles = set()
        for line in cr.fetchall():
            # get the index of the first tax that appears twice
            dup_idx = [i for i, n in enumerate(line[0]) if line[0].count(n) == 2][0] + 1
            # truncate the list to only keep the recurrent part
            cycle = line[0][dup_idx:]
            # rewrite the cycle starting from minimum value of the tax
            min_idx = min(enumerate(cycle), key=itemgetter(1))[0]
            cycle = cycle[min_idx:] + cycle[:min_idx] + [cycle[0]]
            filtered_cycles.add(tuple(cycle))
        raise util.MigrationError(
            f"""There exists cycle(s) in parent tax and child tax.
            This is an issue in configuration, please adapat tax configuration and try to upgrade again.
            Tax(es): {filtered_cycles}"""
        )
