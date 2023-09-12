# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util

# > git -C ~/src/enterprise/master grep 'installable.*True' enterprise/{9..15}.0 -- pos_blackbox_be/__{openerp,manifest}__.py
# enterprise/9.0:pos_blackbox_be/__openerp__.py:    'installable': True,
# enterprise/11.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/13.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/14.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/15.0:pos_blackbox_be/__manifest__.py:    'installable': True,
BLACKBOX_CERTIFIED_VERSIONS = {"9.0", "11.0", "13.0", "14.0", "15.0"}


ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE = util.str2bool(os.getenv("ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE", "0"))


def migrate(cr, version):
    if not ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE and util.module_installed(cr, "pos_blackbox_be"):
        source = os.getenv("ODOO_UPG_DB_SOURCE_VERSION")
        target = os.getenv("ODOO_UPG_DB_TARGET_VERSION")

        # block the upgrade if source version is certified but not target version
        if source in BLACKBOX_CERTIFIED_VERSIONS and target not in BLACKBOX_CERTIFIED_VERSIONS:
            msg = "pos_blackbox_be upgrade to {} is not supported from {}".format(target, source)
            util._logger.critical(msg)
            raise util.MigrationError(msg)

        # warn about upgrading to a certified version
        if source not in BLACKBOX_CERTIFIED_VERSIONS and target in BLACKBOX_CERTIFIED_VERSIONS:
            util._logger.info("pos_blackbox_be will be upgraded to a certified version in %s from %s", target, source)

    # check there are no cycles in partners hierarchy this is not allowed by standard
    # BUT if there is a cycle some computed fields may end up in an infinite loop
    cr.execute(
        """
        WITH RECURSIVE info AS (
            SELECT parent_id AS id,
                   ARRAY[parent_id] AS path,
                   False AS cycle
              FROM res_partner
             WHERE parent_id IS NOT NULL

             UNION ALL

            SELECT child.id AS is,
                   ARRAY_PREPEND(child.id, parent.path) AS path,
                   child.id =ANY(parent.path) AS cycle
              FROM info AS parent
              JOIN res_partner child
                ON child.parent_id = parent.id
             WHERE NOT parent.cycle
        )
        SELECT path FROM info WHERE cycle
       """
    )
    if cr.rowcount:
        # extract the cycle for each path and put it in a summary to report
        res = []
        done = set()
        for path in cr.fetchall():
            seen = {}
            for i, x in enumerate(path):
                if x in done:  # the cycle in this path was already added to the summary
                    break
                if x in seen:
                    res.append(path[seen[x] : i + 1])  # add only the cycle part in path
                    done.update(path)  # all partners in this path already had the cycle identified
                    break
                seen[x] = i
        report = "\n".join((" * " + "->".join("res.partner({})".format(id_) for id_ in path)) for path in res)
        raise util.MigrationError("Cycle detected for the following partners (via `parent_id`):\n{}".format(report))
