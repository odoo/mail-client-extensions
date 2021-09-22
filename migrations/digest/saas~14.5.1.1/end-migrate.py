# -*- coding: utf-8 -*-

from odoo.upgrade.util.jinja_to_qweb import upgrade_jinja_fields


def migrate(cr, version):
    upgrade_jinja_fields(cr, "digest_tip", [], ["tip_description"], model_name="digest.digest")
