Requires registered app on the wargaming devlopers site.
The wargaming python module currently has a bug in the base_urls.
A hacky fix can be applied by changing REGION_API_ENDPOINTS in the
settings.py in the wargaming package to use the new end points.
e.g 'eu': 'https://api.worldofwarships.eu',
