from __future__ import annotations

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface

from hatch_calver.bump import bump_calver


class CalverScheme(VersionSchemeInterface):
    PLUGIN_NAME = "calver"

    def update(self, desired_version: str, original_version: str, version_data: dict) -> str:  # noqa: D102
        if not desired_version:
            return original_version

        version = bump_calver(
            original_version,
            desired_version,
            calver_scheme_string=self.config.get("calver-scheme", "YYYY.MM.DD"),
        )

        if self.config.get("validate-bump", True):
            from packaging.version import Version

            next_version = Version(version)
            if next_version <= Version(original_version):
                msg = f"Version `{version}` is not higher than the original version `{original_version}`"
                raise ValueError(msg)
        return version
