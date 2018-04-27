"""
Bumps model file which loads the fit problem from a sasview saved state.
"""

from bumps.names import *
from sas.sascalc.fit.fitstate import BumpsPlugin
from sas.sascalc.fit.BumpsFitting import BUMPS_DEFAULT_FITTER
from bumps.options import FIT_CONFIG
FIT_CONFIG.selected_id = BUMPS_DEFAULT_FITTER

# Load the fir
problem = BumpsPlugin.load_model(sys.argv[1])
