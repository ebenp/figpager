[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/ambv/black)
[![GitHub Workflow
Status](https://img.shields.io/github/workflow/status/ebenp/figpager/Run%20Tox?style=for-the-badge)](https://github.com/ebenp/figpager/actions)
[![PyPI
version](https://img.shields.io/pypi/v/figpager.svg?style=for-the-badge)](https://pypi.org/project/figpager/)
[![PyPI
pyversions](https://img.shields.io/pypi/pyversions/figpager.svg?style=for-the-badge)](https://pypi.python.org/pypi/figpager/)
[![License:
MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

# FigPager

Python's [Matplotlib](http://matplotlib.org) can save plots with 
various backends and single or multi pages. 
FigPager is a wrapper class for those backends. 

This class reads layout specifications from an .ini file. FigPager 
handles drawing boxes, text, images and lines referenced in .ini files on a figure canvas. 
The class handles adding subplots, adding new pages in multipage backends and closing the figure.

## Install
Install using pip
```
pip install figpager
```

## Usage
After install FigPaper can be imported from figpager
```
from figpager import FigPager
```
A FigPager instance is initialized with a paper size of A0-A10, B0-B10, letter, 
legal or ledger.
```
fp = FigPager(
        "letter",
        3,
        3,
    )
```

Additional keywords provide further functionality.
See the code for all keywords.
```
fp = FigPager(
        "letter",
        3,
        2,
        layout="Report",
        outfile=.\out.pdf,
        orientation="portrait",
        height_ratios=[1, 1, 2],
        overwrite=True,
        transparent=True,
    )
```

with blocks are also supported with no need for fp.close()
```
with FigPager("letter", 3, 2, layout="Report", outfile=.\out.pdf,
        orientation="portrait", height_ratios=[1, 1, 2],
        overwrite=True, transparent=True) as fp:
```

Example layout .ini files can be found in the 
package under page_layout.

FigPager has options to add subplots. See the code for all keywords.
```
ax0 = fp.add_subplot()
```

FigPager also has add page options. In backends that don't 
support multipage a zero padded number is added as a suffix to the file name.

The example below 
specifies the number of rows and columns, 
the orientation and height ratios. 
See the code for all keywords.
```
fp.add_page(
                nrows=3, ncols=2, orientation="portrait", height_ratios=[1, 1, 2]
           )
```

The FigPager instance can be be closed following the example below.
```
fp.close()
```

See the test code under tests for example code.

## Development / Testing
Submit issues and PRs through GitHub. 
Testing is done with tox.


## License
FigPager is released under the MIT license. 
See [LICENSE.md](LICENSE.md) for details.
