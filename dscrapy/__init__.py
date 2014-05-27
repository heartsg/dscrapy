import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()



from twisted import version as _txv
twisted_version = (_txv.major, _txv.minor, _txv.micro)
if twisted_version >= (11, 1, 0):
    optional_features.add('http11')
