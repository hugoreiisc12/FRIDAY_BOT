import subprocess
import sys

if __name__ == '__main__':
    ret = subprocess.run([sys.executable, '-m', 'pytest', '-q'])
    sys.exit(ret.returncode)
