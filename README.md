# HoneyPy
A lightweight, extensible framework managing research data, analyses and provenance. HoneyPy works as a core library in a plugin architecture, a framework of sorts. It is built to fulfill common needs found across many research teams:
- To store
- To anonymise
- To transform
- To analyse
- To summarise
- To manage many datasets and analysis projects on a single machine

In doing so, it employs a functional approach; it sees data as something to be continually transformed, be it through a machine learning model, a post-processing script, or some other means. Many research papers boil down to taking raw data through a series of transformations to get to the final results.

It is not uncommon to see research teams reinvent the wheel in this regard. A centralised, general library is much more beneficial to us. Releases to the core should benefit all packages that inherit from it, and field-specific work, what some might call "application logic", should ideally be decoupled from data management.

Every research team tackles its own questions, whether it be linguistics, medicine, sociology, or something else. It is the job of the core to automate the "boring" stuff, and the job of the plugin to perform the field-specific transformations.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/honeypyteam/honeypy)
