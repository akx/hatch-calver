# hatch-calver

A plugin for [hatch][hatch] to support [calendar versioning][calver].

## Setup

Add `hatch-calver` as a build dependency to your project.

```toml
[build-system]
requires = [
    "hatchling",
    "hatch-calver",
]
build-backend = "hatchling.build"
```

Then, set `tool.hatch.version.scheme` to `"calver"`.

```toml
[tool.hatch.version]
scheme = "calver"
```

### Configuring the CalVer scheme

You can optionally set `calver-scheme` to a dot-separated string
of parts specified in the [calver scheme][calver_scheme] specification.
It defaults to `YYYY.MM.DD`.

```toml
[tool.hatch.version]
scheme = "calver"
calver-scheme = "YY.MM"
```

Note that your project's versions should conform to the scheme you specify;
otherwise, determining where to put e.g. patch versions will be quite ambiguous.

## Usage

You can use Hatch's [standard versioning][hatch_version_updating] commands.

To update your project's version to the current date, run `hatch version release`
(or `hatch version date`).

As with the regular versioning scheme, you can chain multiple segment updates.
The date part of the version will _not_ be updated unless you explicitly specify it.

The CalVer scheme specified for your project specifies which segment of the
PEP 440 "release" segments are automatically determined; for instance, for a `YYYY.MM.DD`
scheme, the 4th field of the release segment will be considered the `patch` field.

In other words, if you specify `YYYY.MM.DD` as your scheme, and it's the 16th of September 2024:

| Original version | Command                 | New version     |
| ---------------- | ----------------------- | --------------- |
| `2024.07.22`     | `hatch version release` | `2024.09.16`    |
| `2024.07.22`     | `hatch version date,a`  | `2024.09.16a0`  |
| `2021.01.01`     | `hatch version rc`      | `2021.01.01rc0` |
| `2024.7.22`      | `hatch version patch`   | `2024.07.22.1`  |

[hatch]: https://hatch.pypa.io/
[hatch_version_updating]: https://hatch.pypa.io/latest/version/#updating
[hatch_version_segments]: https://hatch.pypa.io/latest/version/#supported-segments
[calver]: https://calver.org/
[calver_scheme]: https://calver.org/#scheme
