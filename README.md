# Rigified Blender Addon


## Versioning

Why these weird looking version numbers you ask, say 1.0.0.1.5.1234?

Well, because Blender only supports integers in the version tuple and
no strings.

Yet we want alpha, beta and RC releases and somehow encode this in the
version number.

Also, we want to include the platform and build numbers for addons that
are not pure python. 

Normally, and with semver, you would have a version numbers like e.g.
1.0.0, 1.0.0-1234, 1.0.0-alpha-1-1234 or 1.0.0-RC-1-1234.

So additional fields have been added to the semver based 3 tuple that make
up a standard version number.

A version number conveys the following information

```
<major>.<minor>.<patch>[.<state>.<increment>][.<build-number>]
```

- major
 
  The major release number, a major feature release.

- minor

  The minor release number, a feature release.

- patch

  The patch release number, a maintenance release.

- state

  The state release number, which is omitted for stable releases, as it is always 0.

  - 0 is always the stable release and will be omitted
  - 1 depicts a release in alpha state, or alpha for short
  - 2 depicts a release in beta state, or beta for short
  - 3 depicts a release in release candidate state, or RC for short

- increment

  The state increment release number, which is omitted for stable releases, as it is always 0.

  - 0 is always the stable release increment and will be omitted
  - 1..N the release state increment

- build number

  The build number.


```python
import re
exp = r'^(?P<major>\d+)[.](?P<minor>\d+)[.](?P<patch>\d+)([.](?P<state>\d)[.](?P<increment>\d+))?([.](?P<build>\d+))?$'

```


### Example Version Numbers

- 1.0.0

  a stable release

- 1.0.0.1.2

  the second alpha (1) release increment (2) for future stable release 1.0.0

- 1.0.0.2.5

  the fifth beta (2) release increment (5) for future stable release 1.0.0

- 1.0.0.3.1

  the first release candidate (3) release increment (1) for future stable release 1.0.0

- 1.0.0.1234

  stable release with build number

