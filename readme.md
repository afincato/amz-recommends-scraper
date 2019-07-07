amz recommends scraper
======================

little python scraper to grab “amazon’s recommends“ suggestions data.

## setup

to run the script, the easiest would be to 

- install / use pipenv
- clone the repo
- install the dependencies listed in the `Pipfile`

and then run `pipenv shell` to activate the python environment.

else, simply clone the repo, install the dependencies listed in the `Pipfile` and run the script using `python3`.

## usage

```
$ python main.py <search-term>
```

eg.

```
$ python main.py 'black feminism'
```

## notes

scraping amazon is notoriously a troubled effort, as it often spots for bots and it shows up CAPTCHA forms or other pages rather than the page you are looking for.

apparently, for now setting the following headers values for python’s requests module make it works

```
import requests

requests.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'})
```
