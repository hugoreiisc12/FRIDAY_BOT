import sys, os
ROOT = os.getcwd()
print('CWD=', ROOT)
print('ROOT in sys.path?', ROOT in sys.path)
print('Listing root entries:', os.listdir(ROOT))
print('gravacao_teste and Dependenciais have been removed from this project')
