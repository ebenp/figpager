# Test of Report configuration
import os

# backend for display in GitHub Actions
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.pyplot as plt

from figpager import FigPager

def test_main():
    # Initialize with a configuration that controls page margins
    # and plot spacing
    # Initialize with a page size and number of plots

    # Initialize with an output file
    # plots an image from http://www.metmuseum.org/art/collection/search/334348 CC0 1.0 Public Domain
    outfile = "./tests/out.pdf"
    fp = FigPager(
        "letter",
        3,
        3,
        outfile=outfile,
        overwrite=True,
    )

    # ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3, )
    subplotspec = fp.gs.new_subplotspec((0, 0), colspan=3)
    ax1 = plt.subplot(subplotspec)
    # ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=2)
    subplotspec = fp.gs.new_subplotspec((1, 0), colspan=2)
    ax2 = plt.subplot(subplotspec)
    # ax3 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
    subplotspec = fp.gs.new_subplotspec((1, 2), rowspan=2)
    ax3 = plt.subplot(subplotspec)
    # ax4 = plt.subplot2grid((3, 3), (2, 0))
    subplotspec = fp.gs.new_subplotspec((2, 0))
    ax4 = plt.subplot(subplotspec)
    # ax5 = plt.subplot2grid((3, 3), (2, 1))
    subplotspec = fp.gs.new_subplotspec((2, 1))
    ax5 = plt.subplot(subplotspec)

    print("outfile: " + outfile)
    # close the figure
    fp.close()
    print("--Done!--")


if __name__ == "__main__":
    test_main()
