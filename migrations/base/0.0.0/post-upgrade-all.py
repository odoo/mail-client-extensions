# -*- coding: utf-8 -*-

# Force all installed modules to be upgraded
#
# Despite being do by the update engine, it needs some help for upgrades.
#
# When odoo drill down dependencies to update module state to mark them as
# `to upgrade`, it stops at `to install` modules.
# While it makes sense during a normal update, it's not enough during
# version change, when dependencies change.
#
# These dependencies change can lead to a situation where an installed
# module has only one dependency that happens to be a new module to
# install. As result, this module keeps its `installed` state and is not
# updated.
#
# While the module is still upgraded (I still have to investigate why),
# the `end-` scripts are skipped, which leads to an incomplete upgrade.
#
# This situation happens during the upgrade of `account_asset` from
# `12.0` to `saas~12.3` if `account_reports` wasn't already installed.
# See https://upgradeci.odoo.com/upgradeci/run/1774


def migrate(cr, version):
    cr.execute("UPDATE ir_module_module SET state = 'to upgrade' WHERE state = 'installed'")
