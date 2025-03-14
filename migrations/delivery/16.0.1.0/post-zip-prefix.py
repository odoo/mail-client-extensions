import re
from collections import defaultdict

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    # attempt to convert zip_to - zip_from ranges into prefixes
    # Some cases where this will fail:
    # - zips are different lengths:
    #   This is probably already not filtering as users would expect since it's doing a string
    #   compare, e.g. 100 - 1000, won't allow 200. If we were to assume that they would want the
    #   values inbetween, there's no way to create the prefixes without allowing unintended zips,
    #   e.g.: 1-22, results in [1, 2,..., 9, 20, 21, 22], but these prefixes will allow 23-99.
    #   We additionally don't want to dev a special alg to create the currently filtered values
    #   since this is probably/hopefully an edge case, e.g. 1-31 would need to somehow turn into
    #   [1, 2, 30, 31] and may be confusing to users)
    # - zips with non-alphanumeric/ascii values (excluding separators, i.e. spaces and '-')
    # - zips where zip_from > zip_to
    #
    # Some junk prefixes may also be created by this script, for non-digit zips, but will match
    # original filtering logic. These junk prefixes are due to:
    #   - Some letters [combos] are not being allowed for some countries + some letters represent
    #     specific land regions and others do not => can't write something generic to handle
    #     all the different country standards
    #   - FYI: There appears to only be 6 countries where this applies (A = alpha, # = digit):
    #     (AR) A####AAA, (BN) AA####, (CA) A#A#A#, (MT) AAA####, (NL) ####AA,
    #     plus our "favorite", the UK forms: AA#A#AA, A#A#AA, A##AA, AA##AA, AA###AA.

    def conv_to_prefixes(zip_from, zip_to):
        """
        :param zip_from, zip_to: strings of only ascii alphanum chars
        :return list(string): list of prefixes also in string form
        """

        N = len(zip_from)
        assert len(zip_to) == N

        if zip_from.isnumeric() and zip_to.isnumeric():
            max_digit = "9"
        else:
            zip_from, zip_to = zip_from.upper(), zip_to.upper()
            max_digit = "Z"

        if N == 0 or zip_from > zip_to:
            return []
        if zip_to == zip_from:
            return [zip_to]

        for i in range(N):
            if zip_from[i] != zip_to[i]:
                break
        common = zip_from[:i]  # common part between zips

        # optimization: if f=common00000 and t=common9999
        # then common is the only prefix we need
        if all(zip_from[j] == "0" and zip_to[j] == max_digit for j in range(i, N)):
            return [common]

        middle = [common + c for c in map(chr, range(ord(zip_from[i]) + 1, ord(zip_to[i]))) if c.isalnum()]
        # https://docs.python.org/3/library/string.html#format-specification-mini-language
        # >>> var, w = 'xy', 7
        # >>> f"{var:c<{w}}"
        # 'xyccccc
        left = [common + p for p in conv_to_prefixes(zip_from[i:], f"{zip_from[i]:{max_digit}<{N - i}}")]
        right = [common + p for p in conv_to_prefixes(f"{zip_to[i]:0<{N - i}}", zip_to[i:])]

        return left + middle + right

    def get_separators(zip_code):
        """
        :param zip_code: string which might contain separators (space or '-')
        :return list(tuple): list of (separator, index) tuples
        """

        return [(m.group(0), m.start()) for m in re.finditer("[ -]", zip_code)]

    cr.execute(
        """
        SELECT id, name, zip_from, zip_to
          FROM delivery_carrier
         WHERE zip_from IS NOT NULL
            OR zip_to IS NOT NULL
        """
    )

    failed_conversions = []
    carrier_to_prefixes = defaultdict(list)
    for carrier_id, name, orig_zip_from, orig_zip_to in cr.fetchall():

        def add_failure(name, reason, orig_zip_from=orig_zip_from, orig_zip_to=orig_zip_to):
            failed_conversions.append((name, orig_zip_from, orig_zip_to, reason))

        zip_from, zip_to = (orig_zip_from or "").strip(), (orig_zip_to or "").strip()
        if not zip_from or not zip_to:
            reason = "Missing zip from or to value."
            add_failure(name, reason)
            continue
        if len(zip_from) != len(zip_to):
            reason = (
                "Mismatching zip lengths. Existing zip filtering may not have been applied "
                "as expected since almost no countries have varying zip lengths."
            )
            add_failure(name, reason)
            continue

        seps = get_separators(zip_from)
        if seps != get_separators(zip_to):
            # separators do not match => probably typo since it appears no postcodes have varying
            # separator structures
            reason = "Separator (space or '-') locations do not match in zips and is therefore not convertable."
            add_failure(name, reason)
            continue
        # Determine prefixes without separators, re-add them later
        zip_from = zip_from.replace(" ", "").replace("-", "")
        zip_to = zip_to.replace(" ", "").replace("-", "")

        if not (zip_from.isalnum() and zip_from.isascii()) or not (zip_to.isalnum() and zip_to.isascii()):
            reason = "Non-alphanumeric/ASCII values except for separators (space or '-') are not convertable."
            add_failure(name, reason)
            continue

        new_prefixes = conv_to_prefixes(zip_from, zip_to)
        if seps:
            new_prefixes_sep = []
            for n in new_prefixes:
                for c, idx in seps:
                    if idx >= len(n):
                        break
                    n = n[:idx] + c + n[idx:]
                new_prefixes_sep.append(n)
            new_prefixes = new_prefixes_sep
        carrier_to_prefixes[carrier_id] = new_prefixes

    all_prefixes = sorted(set(prefix for prefixes in carrier_to_prefixes.values() for prefix in prefixes))
    prefixes = env["delivery.zip.prefix"].create([{"name": prefix} for prefix in all_prefixes])
    prefix_to_id = {prefix.name: prefix.id for prefix in prefixes}
    for carrier_id, prefixes in carrier_to_prefixes.items():
        env["delivery.carrier"].browse(carrier_id).write(
            {"zip_prefix_ids": [(6, 0, [prefix_to_id[prefix] for prefix in prefixes])]}
        )

    if failed_conversions:
        msg = """
            <details>
            <summary>
            Some Shipping Methods have 'Zip From' and/or 'Zip To' values that couldn't be
            converted to the new 'Zip Prefixes' option. You will have to manually update these
            shipping methods to recreate the same behavior.
            </summary>
            Here is the list (Shipping Method: Zip From - Zip To. Reason for failure.):
            <ul>
            {}
            </ul>
            </details>
        """.format("\n".join("<li>{}: {} - {}. Reason: {}</li>".format(*t) for t in failed_conversions))

        util.add_to_migration_reports(msg, "Delivery", format="html")

    util.remove_field(cr, "delivery.carrier", "zip_from")
    util.remove_field(cr, "delivery.carrier", "zip_to")
