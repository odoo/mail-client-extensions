#!/usr/bin/env python3

# This tool requires:
# * networkx -> python3 -m install networkx (or your flow's equivalent, uv?)
# * graphviz -> apt install graphviz (or your system's equivalent)
# If you use uv to run this file:
# /// script
# dependencies = [
#   "pydot",
#   "networkx",
# ]
# ///


import argparse
import itertools
import pathlib
import sys
import tempfile
import webbrowser

import networkx

# Legend
legend = r"\l".join(
    """\
Generated for Odoo {}
Legend
 - round = community/themes/industry
 - rectangular = enterprise
 - blue border = requested module
 - blue background = auto install
 - arrow = dependency
 - blue arrow = autoinstall dependency\
""".splitlines()
)


def build_graph(version):
    G = networkx.DiGraph()
    G.add_node(legend, color="white", align="left")
    for addon_dir in itertools.chain(
        version.glob("*/addons/*"),  # base addons
        version.glob("addons/*"),  # community addons
        (version / "../../enterprise" / version.name).glob("*"),
        (version / "../../industry" / version.name).glob("*"),
        (version / "../../design-themes" / version.name).glob("*"),
        (version / "../../themes" / version.name).glob("*"),  # design-themes alias
    ):
        for manifest in (addon_dir / "__manifest__.py", addon_dir / "__openerp__.py"):
            if (
                manifest.is_file()
                and addon_dir.name[0].isalpha()  # avoid . dirs, and __pychache__
                and not addon_dir.name.startswith("test_")  # ignore test_ addons
            ):
                break
        else:
            continue
        repo = next(
            (r for r in ["enterprise", "industry", "design-themes", "themes"] if addon_dir.match(r + "/*/*")), "odoo"
        )
        repo = "design-themes" if repo == "themes" else repo
        info = eval(manifest.read_text(encoding="utf-8"))
        for dep in info.get("depends", {}):
            G.add_edge(addon_dir.name, dep)
            G.nodes[addon_dir.name]["repo"] = repo
            auto_install = info.get("auto_install")
            if isinstance(auto_install, list):
                for aut in auto_install:
                    G.add_edge(addon_dir.name, aut, color="blue")
            G.nodes[addon_dir.name]["auto_install"] = bool(auto_install)
    return G


def get_nodes(G, init_nodes):
    level = list(init_nodes)
    nodes = []
    adj = dict(G.adjacency())
    while level:
        nodes.extend(level)
        level = list(itertools.chain.from_iterable(adj[n].keys() for n in level))
    return nodes


def main(args):
    global legend  # noqa: PLW0603
    path = pathlib.Path(args.src).expanduser() / "odoo" / args.version
    if not path.is_dir():
        raise ValueError(f"Invalid Odoo version '{args.version}'")
    legend = legend.format(args.version)

    G = build_graph(path)
    modules = [module for module in args.modules if module in G]
    invalid = set(args.modules) - set(modules)
    if invalid:
        print(f"Module {invalid} are invalid module for version {args.version.name}")  # noqa: T201
        sys.exit(1)
    nodes = get_nodes(G, modules) if not args.dependants_only else []
    nodes.extend(get_nodes(G.reverse(), args.modules) if args.dependants or args.dependants_only else [])
    G = G.subgraph([*nodes, legend])

    PG = networkx.nx_pydot.to_pydot(G)
    for node, data in G.nodes(data=True):
        if data.get("repo") == "enterprise":
            PG.get_node(node)[0].set_shape("box")
        if data.get("auto_install"):
            PG.get_node(node)[0].set_style("filled")
            PG.get_node(node)[0].set_fillcolor("lightblue")
    for node in modules:
        PG.get_node(node)[0].set_color("blue")

    with tempfile.NamedTemporaryFile(prefix="modules_graph_", suffix=".svg", delete=False) as g_file:
        PG.write_svg(g_file.name)

    webbrowser.open("file://{}".format(g_file.name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shows a graph of dependencies in Odoo modules.")
    parser.add_argument("version", help="Odoo version")
    parser.add_argument("modules", nargs="+", help="Module(s) to visualize")
    parser.add_argument("--src", help="Base src file for all repos", default="~/src")
    parser.add_argument(
        "-d",
        "--dependants",
        help="Show also the modules that depend on this module",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-D",
        "--dependants-only",
        help="Show only the modules that depend on this module",
        action="store_true",
        default=False,
    )

    main(parser.parse_args())
