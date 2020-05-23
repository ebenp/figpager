# Test of adding a subplot in a given location

# Plots from: https://matplotlib.org/3.2.1/gallery/images_contours_and_fields/plot_streamplot.html#sphx-glr-gallery-images-contours-and-fields-plot-streamplot-py

import numpy as np

from figpager import FigPager

# Reference:
# https://matplotlib.org/devdocs/gallery/subplots_axes_and_figures/subplots_demo.html


def test_main():
    # Initalize with a configuration that controls page margins
    # and plot spacing
    # Initalize with a page size and number of plots

    # Initalize with an output file
    outfile = "./tests/out_4.pdf"

    fp = FigPager(
        "letter", 2, 2, outfile=outfile, orientation="portrait", overwrite=True,
    )
    # Some example data to display
    x = np.linspace(0, 2 * np.pi, 400)
    y = np.sin(x ** 2)

    # redraw the page here
    fp.draw_page()

    ax = fp.add_subplot(pos=[1, 1])
    ax.plot(x, y)
    ax.set_title("Plot 1 ")

    ax = fp.add_subplot()
    ax.plot(x, y, "tab:orange")
    ax.set_title("Plot 2")

    ax = fp.add_subplot()
    ax.plot(x, -y, "tab:green")
    ax.set_title("Plot 3")

    ax = fp.add_subplot()
    ax.plot(x, -y, "tab:red")
    ax.set_title("Plot 4")

    # fp.add_page()
    # fp.constrained_layout = True
    # redraw the page here
    # fp.draw_page()

    ax = fp.add_subplot()
    ax.plot(x, y)
    ax.set_title("Plot 1 ")

    ax = fp.add_subplot()
    ax.plot(x, y, "tab:orange")
    ax.set_title("Plot 2")

    ax = fp.add_subplot()
    ax.plot(x, -y, "tab:green")
    ax.set_title("Plot 3")

    ax = fp.add_subplot()
    ax.plot(x, -y, "tab:red")
    ax.set_title("Plot 4")

    print("outfile: " + outfile)
    # close the figure
    fp.close()
    print("--Done!--")


if __name__ == "__main__":
    test_main()
