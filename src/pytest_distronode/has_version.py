"""Fixme."""
import distronode

from pkg_resources import parse_version


has_distronode_v2 = parse_version(distronode.__version__) >= parse_version("2.0.0")
has_distronode_v24 = parse_version(distronode.__version__) >= parse_version("2.4.0")
has_distronode_v28 = parse_version(distronode.__version__) >= parse_version(
    "2.8.0.dev0",
) or parse_version(distronode.__version__) >= parse_version("2.8.0")
has_distronode_v29 = parse_version(distronode.__version__) >= parse_version("2.9.0")
has_distronode_v212 = parse_version(distronode.__version__) >= parse_version("2.12.0")
has_distronode_v213 = parse_version(distronode.__version__) >= parse_version("2.13.0")
