import datetime

import pytest

from hatch_calver.bump import bump_calver

DT = datetime.datetime(2024, 9, 16, 13, 48, tzinfo=datetime.timezone.utc)

cases = [
    # Test that `release`/`date` instructions update the date part to the current date
    ("0", "release", "2024.9.16", "YYYY.MM.DD"),
    ("0", "date", "2024.09.16", "YYYY.0M.DD"),
    ("0.0", "date", "24.38", "YY.WW"),
    # Test patch
    ("2024.09.16", "patch", "2024.09.16.1", "YYYY.0M.DD"),
    ("2024.09.16.1", "patch", "2024.09.16.2", "YYYY.0M.DD"),
    # Test prereleases
    ("2024.09.16", "a,alpha", "2024.09.16a1", "YYYY.0M.DD"),
    ("2024.09.16", "b,beta,b", "2024.09.16b2", "YYYY.0M.DD"),
    ("2024.09.16", "c,pre,rc", "2024.9.16rc2", "YYYY.M.DD"),  # pre = rc in PEP440 terms
    # Test postreleases
    ("2024.09.16", "post,rev,r", "2024.09.16.post2", "YYYY.0M.DD"),
    # Test dev
    ("2024.09.16", "dev", "2024.9.16.dev0", "YYYY.M.DD"),
    # Weird long instructions
    ("2024.09.16.42", "patch,micro,fix,post,post", "2024.09.16.45.post1", "YYYY.0M.DD"),
    ("2024.09.10.1.post3", "date,patch,micro,fix,post,post", "24.09.16.4.post1", "YY.0M.DD"),
    # Cases which do not update the date part (`release`/`date` not specified)
    ("2023", "patch", "2023.1", "YYYY"),
    ("2023.12", "patch", "2023.12.1", "YYYY.MM"),
    # Test that we re-pad packaging.Version-mangled bits
    ("2024.9.3", "patch", "2024.09.03.1", "YYYY.0M.0D"),
    # Test simply setting the version
    ("0", "2024.1.1", "2024.1.1", "this won't matter"),
]


@pytest.mark.parametrize(("original_version", "desired_version", "expected", "scheme"), cases)
def test_bump(original_version, desired_version, expected, scheme):
    calver = bump_calver(original_version, desired_version, calver_scheme_string=scheme, version_date=DT)
    assert calver == expected


def test_smoke():
    # Just exercises the "no date set" path – we can't know what the date will be
    assert bump_calver("0", "date")


def test_bad_spec():
    with pytest.raises(ValueError, match="Unknown calver-scheme part"):
        assert bump_calver("0", "date", calver_scheme_string="HEY.THERE")


def test_bad_multiple_instructions():
    with pytest.raises(ValueError, match="Cannot specify multiple"):
        assert bump_calver("0", "2024.8.15,patch")
