# Parts of this code has been adapted from the Hatchling project's
# `hatchling.version.scheme.standard` module, which is licensed under
# the MIT License (Copyright (c) 2017-present Ofek Lev <oss@ofek.dev>).

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packaging.version import Version

SCHEME_PART_TO_FORMATTER = {
    # See https://calver.org/#scheme
    "YYYY": lambda d: d.year,
    "YY": lambda d: d.year - 2000,
    "0Y": lambda d: f"{d.year % 100:02}",
    "MM": lambda d: d.month,
    "0M": lambda d: f"{d.month:02}",
    "WW": lambda d: d.isocalendar()[1],
    "0W": lambda d: f"{d.isocalendar()[1]:02}",
    "DD": lambda d: d.day,
    "0D": lambda d: f"{d.day:02}",
}

SCHEME_PART_MIN_LENGTHS = {
    "YYYY": 4,
    "YY": 2,
    "0D": 2,
    "0M": 2,
    "0W": 2,
    "0Y": 2,
}


def _map_scheme_part(part: str, dt: datetime.datetime) -> str:
    formatter = SCHEME_PART_TO_FORMATTER.get(part)
    if formatter is None:
        err = f"Unknown calver-scheme part: {part} (expected one of {', '.join(SCHEME_PART_TO_FORMATTER)})"
        raise ValueError(err)

    return str(formatter(dt))


def _update_version(version: Version, **kwargs: Any) -> None:
    parts = {}
    for part_name in ("epoch", "release", "pre", "post", "dev", "local"):
        if part_name in kwargs:
            parts[part_name] = kwargs[part_name]
        elif parts:  # We've set a part, so clear out the following ones
            parts[part_name] = None

    version._version = version._version._replace(**parts)


def bump_calver(
    original_version: str,
    desired_version: str,
    *,
    calver_scheme_string: str = "YYYY.MM.DD",
    version_date: datetime.datetime | None = None,
) -> str:
    """Bumps a CalVer version according to the given instructions."""
    from packaging.version import Version
    from packaging.version import _parse_letter_version as parse_letter_version

    if not version_date:
        version_date = datetime.datetime.now(tz=datetime.timezone.utc)

    scheme_parts = str(calver_scheme_string).split(".")
    v = Version(original_version)
    instructions = desired_version.split(",")
    for inst in instructions:
        if inst in {"date", "release"}:
            # Update the prefix of the current `release`,
            # but keep the remaining (non-specified) parts as-is.
            release = (
                *(_map_scheme_part(part, version_date) for part in scheme_parts),
                *v.release[len(scheme_parts) :],
            )
            v._version = v._version._replace(release=release)
            _update_version(v, release=release)
        elif inst in {"micro", "patch", "fix"}:
            # We'll assume the first part after any part specified by the calver scheme is the micro/patch/fix part.
            old_micro = v.release[len(scheme_parts)] if len(v.release) > len(scheme_parts) else 0
            new_release = (*v.release[: len(scheme_parts)], old_micro + 1)
            _update_version(v, release=new_release)
        elif inst in {"a", "b", "c", "rc", "alpha", "beta", "pre", "preview"}:
            phase, number = parse_letter_version(inst, 0)
            if v.pre:
                current_phase, current_number = parse_letter_version(*v.pre)
                if phase == current_phase:
                    number = current_number + 1

            _update_version(v, pre=(phase, number))
        elif inst in {"post", "rev", "r"}:
            number = 0 if v.post is None else v.post + 1
            _update_version(v, post=parse_letter_version(inst, number))
        elif inst == "dev":
            number = 0 if v.dev is None else v.dev + 1
            _update_version(v, dev=(inst, number))
        else:
            if len(instructions) > 1:
                msg = "Cannot specify multiple update operations with an explicit version"
                raise ValueError(msg)
            return str(inst)
    # Small hack – `packaging.Version` strips leading zeroes from the release part, so
    # check if we need to pad any of them. This technically breaks the type annotations of
    # `packaging._Version`, but `Version.__str__()` doesn't mind...
    v._version = v._version._replace(
        release=(
            tuple(
                str(val).zfill(SCHEME_PART_MIN_LENGTHS.get(scheme_parts[i], 1))
                if i < len(scheme_parts)
                else val
                for (i, val) in enumerate(v._version.release)
            )
        ),
    )
    return str(v)
