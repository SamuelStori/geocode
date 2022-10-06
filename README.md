
# Geocoder for stori data

We use this to get lat, lon from data. The code iterate over all the geocoders in `geopy` and tries to get the data. Then, if that particular service doesn't work or throw some exceptions, it will try with another one. 


## To run the sript:
1. `conda env create -f environment.yml`
2. `conda activate geocoder`
3. `python get_geolocation_v2.py`


# TODO:
1. This is one first example, obviously we need to get rid of the lists in the main fuction.
2. See the reason of failures in particular geocoders.
    - Maybe some services are failling because the constructor needs extra parameters.  
3. Explore bulk invokations.
    - The caveat here would be that not a lot of services allow bulk requests so we would need to look into the Terms of Usage of every single one.
4. Explore pandas usage: https://geopy.readthedocs.io/en/stable/index.html#usage-with-pandas


## Contributors:
Dillan Aguirre, Eduardo Celis, Eduardo Abreu, Ivan Guerrero.
