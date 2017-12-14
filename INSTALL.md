How to install
==============

1. Create a virtual environment and activate it

       virtualenv venv --no-site-packages
       source venv/bin/activate


2. Install required packages

       pip install -r requirements.txt 


3. Setup required Open Exoplanet Repositories in this directory (clone them here or put a symbolic link to whereever you have them stored)

       git clone git@github.com:OpenExoplanetCatalogue/open_exoplanet_catalogue.git
       git clone git@github.com:OpenExoplanetCatalogue/oec_meta.git
