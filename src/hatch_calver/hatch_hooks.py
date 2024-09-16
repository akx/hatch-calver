from hatchling.plugin import hookimpl


@hookimpl
def hatch_register_version_scheme() -> None:  # noqa: D103
    from hatch_calver.calver_scheme import CalverScheme

    return CalverScheme
