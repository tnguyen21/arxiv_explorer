2024-04-02

- stole the code from arvivscraper on github
  - thin wrapper around urllib calls and xml parsing anyway, cleaned up some bits that seemed unnecessary
- more than 160_000 papers on initial run -- and it timed out!
- tons of CS papers pre-printed on arxiv

- some initial thoughts and problems:

  - exciting! lots of data to work with, will be some mildly interesting challenges
  - how to filter out low quality pre-prints?
  - what categories to include (should I be open to papers from non-ai related categories? probably?)
  - summary statistics?

- next steps:
  - get data all together in one dataframe, create a singular csv with all the papers from the categories im interested in
  - get a sense of scale of data we're working with
  - figure out how to paragraph2vec abstracts quickly
    - might be okay to just use a framework?
    - google also provides some embedding models "out of the box"
