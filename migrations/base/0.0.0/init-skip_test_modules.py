# -*- coding: utf-8 -*-


def prepare_migration(cr):
    # While parsing the test_lint module Odoo tries to import the "astroid"
    # package which is not available in the upgrade container, which makes
    # the upgrade fail with a ModuleNotFoundError.
    # Changing its state excludes the module from the test suite so the
    # problematic file is never parsed.
    cr.execute(
        """
        UPDATE ir_module_module
           SET state='skip'
         WHERE name='test_lint'
           AND state='installed'
        """
    )
