# Thesis.io APIs

Thesis API in Python

## Installation

```bash
pip install thesis_py
```

## Usage

Import the package and initialize the Thesis client with your API key:

```python
from thesis_py import Thesis

thesis = Thesis(api_key="your-api-key")
```

## Common requests

```python

  # basic search
  results = thesis.search("This is a Thesis.io query:")

  # keyword search (non-neural)
  results = thesis.search("Google-style query", type="keyword")

  # search with date filters
  results = thesis.search("This is a Thesis.io query:", start_published_date="2019-01-01", end_published_date="2019-01-31")

  # search with domain filters
  results = thesis.search("This is a Thesis.io query:", include_domains=["www.cnn.com", "www.nytimes.com"])

  # search and get text contents
  results = thesis.search_and_contents("This is a Thesis.io query:")

  # search and get contents with contents options
  results = thesis.search_and_contents("This is a Thesis.io query:",
                                    text={"include_html_tags": True, "max_characters": 1000})

  # find similar documents
  results = thesis.find_similar("https://example.com")

  # find similar excluding source domain
  results = thesis.find_similar("https://example.com", exclude_source_domain=True)

  # find similar with contents
  results = thesis.find_similar_and_contents("https://example.com", text=True)

  # get text contents
  results = thesis.get_contents(["tesla.com"])

  # get contents with contents options
  results = thesis.get_contents(["urls"],
                             text={"include_html_tags": True, "max_characters": 1000})

  # basic answer
  response = thesis.answer("This is a query to answer a question")

  # answer with full text
  response = thesis.answer("This is a query to answer a question", text=True)

  # answer with streaming
  response = thesis.stream_answer("This is a query to answer:")

  # Print each chunk as it arrives when using the stream_answer method
  for chunk in response:
    print(chunk, end='', flush=True)

  # research task example – answer a question with citations
  # Example prompt & schema inspired by the TypeScript example.
  QUESTION = (
      "Summarize the history of San Francisco highlighting one or two major events "
      "for each decade from 1850 to 1950"
  )
  OUTPUT_SCHEMA: Dict[str, Any] = {
      "type": "object",
      "required": ["timeline"],
      "properties": {
          "timeline": {
              "type": "array",
              "items": {
                  "type": "object",
                  "required": ["decade", "notableEvents"],
                  "properties": {
                      "decade": {
                          "type": "string",
                          "description": 'Decade label e.g. "1850s"',
                      },
                      "notableEvents": {
                          "type": "string",
                          "description": "A summary of notable events.",
                      },
                  },
              },
          },
      },
  }
  resp = thesis_py.research..create_task(
      instructions=QUESTION,
      model="thesis-research",
      output_schema=OUTPUT_SCHEMA,
  )
```
