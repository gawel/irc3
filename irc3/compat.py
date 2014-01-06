# -*- coding: utf-8 -*-
import sys
PY3 = bool(sys.version_info[0] == 3)

if PY3:  # pragma: no cover
    text_type = str
    string_types = (bytes, str)
else:  # pragma: no cover
    text_type = unicode
    string_types = basestring
