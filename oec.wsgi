#activate_this = '/home/rein/open_exoplanet_catalogue/venv/bin/activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, '/home/rein/oec_web/')
from oec_web import app as application
