.. figure:: http://i.imgur.com/BkjfI3k.png
   :alt: Skybeard
Introduction
============

Skybeard is a plug-in based bot for telegram, and uses the telepot library.


How to make a beard: quick version
----------------------------------

If you're interested in making a new beard, the easiest way is through the `new_beard.py` script found in the `utils` folder.

.. code-block:: none
  $ utils/newbeard.py -h                              
  usage: newbeard.py [-h] [-d DIR] [-r [REQUIREMENTS [REQUIREMENTS ...]]] name

  Create new beard in given folder.

  positional arguments:
    name                  Name of beard.

  optional arguments:
    -h, --help            show this help message and exit
    -d DIR, --dir DIR     Directory to put beard in (defaults to beard name).
    -r [REQUIREMENTS [REQUIREMENTS ...]], --requirements [REQUIREMENTS [REQUIREMENTS ...]]
                          Create requirements file with optional requirements.

This script will create a new beard, e.g. 

.. code-block:: none
  $ utils/newbeard.py foo_beard                    
  $ tree foo_beard          
  foo_beard
  ├── python
  │   └── foo_beard
  │       └── __init__.py
  ├── README.txt
  └── setup_beard.py

  2 directories, 3 files

which you can run immediately by adding it to the config in the normal way.
