# -*- coding: utf-8 -*-
from contextlib import closing
import csv

from odoo.models import Model
from odoo.addons.base.maintenance.migrations import util
from odoo.tools import file_open

class Partner(Model):
    _inherit = "res.partner"
    _module = "base"

    def _display_address_depends(self):
        # avoid recomputing address of partners when updating country states
        return []


def migrate(cr, version):
    eb = util.expand_braces
    # China
    cn = (
        "BJ SH ZJ TJ AH FJ CQ JX SD HA NM HB XJ HN NX GD XZ "
        "HI GX SC HE GZ SX YN LN SN JL GS HL QH JS TW HK MO"
    )
    for state in cn.split():
        util.rename_xmlid(cr, "l10n_cn.state_" + state, "base.state_cn_" + state)

    # UK
    for state in range(1, 120):
        util.rename_xmlid(cr, "l10n_uk.state_uk_%s" % state, "base.state_uk%s" % state)

    # Romania
    ro = (
        "AB AG AR B BC BH BN BR BT BV BZ CJ CL CS CT CV DB DJ GJ GL GR "
        "HD HR IF IL IS MH MM MS NT OT PH SB SJ SM SV TL TM TR VL VN VS"
    )
    for state in ro.split():
        util.rename_xmlid(cr, *eb("{l10n_ro,base}.RO_" + state))

    # Ethiopia
    for state in range(1, 12):
        util.rename_xmlid(cr, *eb("{l10n_et,base}.state_et_%s" % state))

    # Ireland
    for state in range(1, 33):
        util.rename_xmlid(cr, *eb("{l10n_ie,base}.state_ie_%s" % state))

    # Netherlands
    nl = "dr fl fr ge gr li nb nh ov ut ze zh bq1 bq2 bq3"
    for state in nl.split():
        util.rename_xmlid(cr, *eb("{l10n_nl,base}.state_nl_%s" % state))

    # Turkey
    for state in range(1, 82):
        util.rename_xmlid(cr, *eb("{l10n_tr,base}.state_tr_%02d" % state))

    # Vietnam
    vn = (
        "44 57 31 54 53 55 56 58 43 40 50 04 59 CT 71 33 DN 39 72 45 30 "
        "14 SG 61 73 03 HN 63 HP 23 66 47 34 28 41 02 01 35 09 22 18 67 "
        "36 68 32 24 13 27 29 25 05 52 20 46 21 69 37 07 26 51 49 70 06"
    )
    for state in vn.split():
        util.rename_xmlid(cr, *eb("{l10n_vn,base}.state_vn_VN-%s" % state))

    # Costa Rica
    costa_state = "SJ A H C P G L"
    for state in costa_state.split():
        util.rename_xmlid(cr, *eb("{l10n_cr,base}.state_%s" % state))

    # Dominican Republic
    util.rename_xmlid(cr, "l10n_do.state_DO_4", "base.state_DO_04")
    for state in range(1, 33):
        util.rename_xmlid(cr, *eb("{l10n_do,base}.state_DO_%02d" % state))

    # Peru
    pass  # new data

    # Chile
    pass  # new data

    # Step 2: Try to match existing states to avoid duplicate entries (and constraint violations)
    with closing(file_open("addons/base/data/res.country.state.csv")) as fp:
        reader = csv.reader(fp)
        next(reader)  # remove header line
        for xmlid, cc, _name, code in reader:
            util.ensure_xmlid_match_record(
                cr, "base." + xmlid, "res.country.state", {"country_id": util.ref(cr, "base." + cc), "code": code}
            )
