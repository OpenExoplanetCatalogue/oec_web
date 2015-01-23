activate_this = '/home/hanno/public_html/exoplanet.hanno-rein.de/oec_api/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, '/home/hanno/public_html/exoplanet.hanno-rein.de/oec_api/')
from oec_api import app as application
