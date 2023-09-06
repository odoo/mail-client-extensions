# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util

# > git -C ~/src/enterprise/master grep 'installable.*True' enterprise/{9..15}.0 -- pos_blackbox_be/__{openerp,manifest}__.py
# enterprise/9.0:pos_blackbox_be/__openerp__.py:    'installable': True,
# enterprise/11.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/13.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/14.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/15.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/16.0:pos_blackbox_be/__manifest__.py:    'installable': True,
BLACKBOX_CERTIFIED_VERSIONS = {"9.0", "11.0", "13.0", "14.0", "15.0", "16.0"}


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
