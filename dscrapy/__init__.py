import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()

# WARNING: optional_features set is deprecated and will be removed soon. Do not use.
optional_features = set()
# TODO: backwards compatibility, remove for Scrapy 0.20
optional_features.add('ssl')
try:
    import boto
    del boto
except ImportError:
    pass
else:
    optional_features.add('boto')
try:
    import django
    del django
except ImportError:
    pass
else:
    optional_features.add('django')



from twisted import version as _txv
twisted_version = (_txv.major, _txv.minor, _txv.micro)
if twisted_version >= (11, 1, 0):
    optional_features.add('http11')
