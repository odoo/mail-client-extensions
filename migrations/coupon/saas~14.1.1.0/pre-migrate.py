# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_coupon"):
        util.rename_xmlid(cr, *util.expand_braces("{coupon,sale_coupon}.mail_template_sale_coupon"))
    else:
        util.remove_record(cr, "coupon.mail_template_sale_coupon")
