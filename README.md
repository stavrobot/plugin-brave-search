# Brave search plugin

A Stavrobot plugin that searches the web using the [Brave Search LLM Context API](https://api.search.brave.com/app/documentation/web-search). Returns relevant snippets, titles, and URLs for a given query.

## Installation

Tell Stavrobot to install this plugin:

> Install the plugin at https://github.com/stavrobot/plugin-brave-search

Then configure it with your Brave Search API subscription token:

> Configure the brave-search plugin with API key `<your key>`

You can get a subscription token from [Brave Search API](https://brave.com/search/api/).

## Tools

### search

Search the web and return relevant results with snippets.

**Parameters:**

- `query` (string, required): The search query.

### brave_answer

Ask a question and get an AI-generated answer backed by Brave web search.

**Parameters:**

- `question` (string, required): The question to answer.
