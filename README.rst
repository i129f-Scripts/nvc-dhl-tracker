.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/nvc-dhl-tracker.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/nvc-dhl-tracker
    .. image:: https://readthedocs.org/projects/nvc-dhl-tracker/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://nvc-dhl-tracker.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/nvc-dhl-tracker/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/nvc-dhl-tracker
    .. image:: https://img.shields.io/pypi/v/nvc-dhl-tracker.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/nvc-dhl-tracker/
    .. image:: https://img.shields.io/conda/vn/conda-forge/nvc-dhl-tracker.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/nvc-dhl-tracker
    .. image:: https://pepy.tech/badge/nvc-dhl-tracker/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/nvc-dhl-tracker
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/nvc-dhl-tracker

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

===============
nvc-dhl-tracker
===============


    Automatically track and record records for NVC shipments!


Installation
============

::

    pip install nvc-dhl-tracker

Or clone from github and run

::

     pip install -e "."

Usage
=====

- Follow the gspread documentation to create a service account: https://docs.gspread.org/en/latest/
- Copy the URL of the google spreadsheet
- Create a new sheet in the document and copy the ID out of the URL, this will be the tracking sheet ID.

Then run

::

    i129f_nvc_tracker

And answer the questions it asks. You should be able to let this run indefinitely, but eventually the database will fill up.

As a SystemD service
--------------------

::

   [Unit]
   Description=i129f SystemD Service

   [Service]
   ExecStart=/root/i129fvenv/bin/python -m i129f.nvc_dhl_tracker.cli --no-input --dhl-keys [..., ...] --start-number [...] --google-spreadsheet-url [...] --google-sheet-id [...]
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target

* **no-input**: This disables any input from the command, so that it won't interrupt a daemonized service
* **dhl-keys**: The keys to use with the DHL API
* **start-number**: The number from which to start polling
* **google-spreadsheet-url**: The URL of the Google spreadsheet
* **google-sheet-id**: The ID of the sheet in the spreadsheet to use. This is appended to the URL if you view the spreadsheet in your browser.

You have 1 DHL keys setup, do you want to remove them?
If you want to add new DHL API keys enter them now, leave blank when finished:
Starting at JD0030110676223010
What is the google spreadsheet URL? https://docs.google.com/spreadsheets/d/1Qs7_BaMRvUzr11YNc4b_JxahToGTf3knXFt_9Tjh5-c/
What is the google sheet id? 692605677


.. _pyscaffold-notes:

Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
changes::

    pip install pre-commit
    cd nvc-dhl-tracker
    pre-commit install

It is a good idea to update the hooks to the latest version::

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/

Note
====

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
