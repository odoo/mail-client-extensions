import re

import markupsafe
from lxml import etree

from odoo.upgrade import util


def fix(arch):
    try:
        etree.fromstring(arch)
    except etree.XMLSyntaxError as e:
        m = re.match(r"Unescaped '(.)' not allowed in attributes values, line ([0-9]+), column ([0-9]+)", e.args[0])
        if m:
            char, line_s, column_s = m.groups()
            line = int(line_s) - 1
            column = int(column_s) - 1
            lines = arch.splitlines()
            lines[line] = lines[line][:column] + str(markupsafe.escape(char)) + lines[line][column + 1 :]
            new_arch = "".join(lines)
            refixed = fix(new_arch)
            if refixed is not None:
                return refixed
            return new_arch
    return None


def migrate(cr, version):
    # For unknow reason, some dashboards are wrongly formated. Try to fix them.
    queries = []
    cr.execute("SELECT id, arch FROM ir_ui_view_custom")
    for bid, arch in cr.fetchall():
        new_arch = fix(arch)
        if new_arch:
            queries.append(cr.mogrify("UPDATE ir_ui_view_custom SET arch = %s WHERE id = %s", [new_arch, bid]).decode())

    if queries:
        util.parallel_execute(cr, queries)
