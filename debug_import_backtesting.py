import importlib
m = importlib.import_module('backtesting')
print('module file:', m.__file__)
print('has Backtester:', hasattr(m, 'Backtester'))
print('Backtester repr:', repr(m.__dict__.get('Backtester')))
print('public names:', [k for k in m.__dict__.keys() if not k.startswith('_')])
