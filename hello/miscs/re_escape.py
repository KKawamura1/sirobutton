# Copyright © 2018 Keigo Kawamura
# This source code is part of the following project.
# See: https://github.com/WeblateOrg/weblate
#
#
# Copyright © 2012 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

ESCAPED = frozenset('.\\+*?[^]$(){}=!<>|:-\000')


def re_escape(pattern: str) -> str:
    """Escape for use in database regexp match.

    This is based on re.escape, but that one escapes too much.
    """
    s = list(pattern)
    for i, c in enumerate(pattern):
        if c in ESCAPED:
            if c == "\000":
                s[i] = "\\000"
            else:
                s[i] = "\\" + c
    return "".join(s)
