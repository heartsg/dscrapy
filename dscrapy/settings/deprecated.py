import warnings
from dscrapy.exceptions import DScrapyDeprecationWarning

DEPRECATED_SETTINGS = [
]


def check_deprecated_settings(settings):
    deprecated = [x for x in DEPRECATED_SETTINGS if settings[x[0]] is not None]
    if deprecated:
        msg = "You are using the following settings which are deprecated or obsolete"
        msg = msg + "\n    " + "\n    ".join("%s: %s" % x for x in deprecated)
        warnings.warn(msg, DScrapyDeprecationWarning)
