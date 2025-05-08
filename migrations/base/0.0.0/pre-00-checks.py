# -*- coding: utf-8 -*-
import os

from odoo.release import series

from odoo.addons.base.maintenance.migrations import util

# > git -C ~/src/enterprise/master grep 'installable.*True' enterprise/{9..15}.0 -- pos_blackbox_be/__{openerp,manifest}__.py
# enterprise/9.0:pos_blackbox_be/__openerp__.py:    'installable': True,
# enterprise/11.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/13.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/14.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/15.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/16.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/17.0:pos_blackbox_be/__manifest__.py:    'installable': True,
# enterprise/18.0:pos_blackbox_be/__manifest__.py:    'installable': True,
MULTI_COMPANY_CERTIFIED_BLACKBOX = {"9.0", "11.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "saas~18.2"}
SINGLE_COMPANY_CERTIFIED_BLACKBOX = {"saas~17.2", "saas~17.4"}


ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE = util.str2bool(os.getenv("ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE", "0"))


def migrate(cr, version):
    source = os.getenv("ODOO_UPG_DB_SOURCE_VERSION")
    target = os.getenv("ODOO_UPG_DB_TARGET_VERSION")
    if util.on_CI() and source is None and target is None:
        source = os.environ["ODOO_UPG_DB_SOURCE_VERSION"] = ".".join(version.split(".")[:2])
        target = os.environ["ODOO_UPG_DB_TARGET_VERSION"] = series
    if not ODOO_UPG_FORCE_POS_BLACKBOX_BE_UPGRADE and util.module_installed(cr, "pos_blackbox_be"):
        cr.execute("SELECT COUNT(*)>1 FROM res_company")
        is_multi_company = cr.fetchone()[0]

        # Historically, any user using pos_blackbox_be in a version prior to 17.0 could
        # use the multi-company feature. SPF asked us to remove this feature, so we blocked
        # it in saas-only versions, so that we can still support multi-company users in major versions.
        if is_multi_company:
            BLACKBOX_CERTIFIED_VERSIONS = MULTI_COMPANY_CERTIFIED_BLACKBOX
        else:
            BLACKBOX_CERTIFIED_VERSIONS = SINGLE_COMPANY_CERTIFIED_BLACKBOX | MULTI_COMPANY_CERTIFIED_BLACKBOX

        # block the upgrade if source version is certified but not target version
        if source in BLACKBOX_CERTIFIED_VERSIONS and target not in BLACKBOX_CERTIFIED_VERSIONS:
            msg = "pos_blackbox_be upgrade to {} is not supported from {}".format(target, source)
            util._logger.critical(msg)
            raise util.MigrationError(msg)

        # warn about upgrading to a certified version
        if source not in BLACKBOX_CERTIFIED_VERSIONS and target in BLACKBOX_CERTIFIED_VERSIONS:
            util._logger.info("pos_blackbox_be will be upgraded to a certified version in %s from %s", target, source)

        if series == "18.0":
            util.add_to_migration_reports(
                message="Starting 18.0, once a device opens a certified Point of Sale, it will not be able to open a non-certified Point of Sale anymore.",
                category="POS Blackbox",
            )
