

## Python code that can be run either in command line or GitHub Actions


Fetches available snapshots for users

Fetches specific snapshots that are 200 and JSON headers, saves file as JSON locally

1. Total number of datasets
2. Count and list of datasets not listed in data.json compared between each snapshot and oldest/newest
3. Count and list of datasets newly listed in data.json compared between each snapshot and oldest/newest
4. Count and list of datasets whose link type ____ 404s or otherwise not available.
5. Count and list of datasets file versus URL ending in URL.

#### QUESTION
Users has to decide what dates to use.... 

OR

Compare one in prior administration to whatever latest is?

OR 

Compare one in May, November, December, January 30, to LATEST (if available)

Runs comparisons of JSONs, find statistics

## JavaScript

Make visual to communicate to others:

#### Be able to answer 

1. What are new datasets
2. What are edited datasets
3. What are no longer listed datasets
4. What are 404ing datasets
5. What are newly 404ing datasets
6. What are newly not 404ing datasets


Be able to see high level answer to:
- What datasets were taken out of listing (and might want to see if they still exist and could be backed up?)
- What datasets are still in listing but have URLs that are 404ing... and might be worthy targets to be backed up?
- Provide based on text analysis list of datasets that might be targeted? 

## NOTES

https://github.com/seperman/deepdiff/issues/203

## Proposed Running experience

Be able to do results for multiple agencies in different folders?

Be able to run data collections via GitHub Actions

Next steps would be to see if dataset looks like it was completely gone or just landing page

....and maybe should be backed up if not already.

....and identify where to programmatically back up datasets that are simple files
....and separate from those that are more likely systems
....as well to just see version changes and updates over time and degradation over time as links rot, etc.


### Tactical bits

- Central file that is YAML that holds things like:
    - agency data.json link
    - agency data.json page for web archive
    - dates to pull in list
    - folder paths
    - whether to re-harvest dates if they already exist

- Documentation:
    - ?

- Python files:
    - first levels files that hold lower-level functions
    - second level files that call multiple lower-level functions or put arguments in them

- data folders:
    - Need to be able to call multiple agencies.

- JavaScript/HTML/CSS:
    - Visualize any data...ideally most on single webpage but ability to dig in as well.

### resources

https://resources.data.gov/resources/inventory-data-gov-guide/

https://inventory.data.gov/organization/

https://resources.data.gov/resources/dcat-us/#USG-note

https://catalog.data.gov/report/metrics-dashboard/epa-gov

https://catalog.data.gov/report/metrics-dashboard/epa-gov?format=json

metrics for updates per organizations: https://catalog.data.gov/report/metrics-dashboard/epa-gov?format=json

https://catalog.data.gov/organization/epa-gov

https://github.com/cisagov/dotgov-data

https://github.com/GSA/federal-website-index

https://catalog.data.gov/organization/ed-gov

https://data.ed.gov/data.json


## Min:

Explain how useful:
1. Any deletions that map to 404s since administration change?
2. Where has degredation occurred?

## Future

3. Where are there partial 404s that might suggest partial deletion?
4. Which are systems vs. files

Example notebook or CLI based docs