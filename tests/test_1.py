# Test for multipage support

# Plots from: https://matplotlib.org/3.2.1/gallery/images_contours_and_fields/plot_streamplot.html#sphx-glr-gallery-images-contours-and-fields-plot-streamplot-py
import os

import numpy as np

from figpager import FigPager


def test_main():
    # Initalize with a configuration that controls page margins
    # and plot spacing
    # Initalize with a page size and number of plots

    # Initalize with an output file
    outfile = "./tests/figpager.png"

    # plots an image from http://www.metmuseum.org/art/collection/search/334348 CC0 1.0 Public Domain
    fp = FigPager(
        "letter",
        3,
        2,
        layout="Report",
        outfile=outfile,
        orientation="portrait",
        height_ratios=[1, 1, 2],
        overwrite=True,
        transparent=False,
    )
    for r in range(1):
        if r > 0:
            fp.add_page(
                nrows=3, ncols=2, orientation="portrait", height_ratios=[1, 1, 2]
            )
        w = 3
        Y, X = np.mgrid[-w:w:100j, -w:w:100j]
        U = -1 - X ** 2 + Y
        V = 1 + X - Y ** 2
        speed = np.sqrt(U ** 2 + V ** 2)

        ax0 = fp.add_subplot()
        ax0.streamplot(X, Y, U, V, density=[0.5, 1])
        ax0.set_title("Varying Density")

        fp.text_from_label("Figure Title", "Figure 1")

        # Varying color along a streamline
        ax1 = fp.add_subplot()
        strm = ax1.streamplot(X, Y, U, V, color=U, linewidth=2, cmap="autumn")
        fp.fig.colorbar(strm.lines)
        ax1.set_title("Varying Color")

        #  Varying line width along a streamline
        ax2 = fp.add_subplot()
        lw = 5 * speed / speed.max()
        ax2.streamplot(X, Y, U, V, density=0.6, color="k", linewidth=lw)
        ax2.set_title("Varying Line Width")

        # Controlling the starting points of the streamlines
        seed_points = np.array([[-2, -1, 0, 1, 2, -1], [-2, -1, 0, 1, 2, 2]])

        ax3 = fp.add_subplot()
        strm = ax3.streamplot(
            X, Y, U, V, color=U, linewidth=2, cmap="autumn", start_points=seed_points.T
        )
        fp.fig.colorbar(strm.lines)
        ax3.set_title("Controlling Starting Points")

        # Displaying the starting points with blue symbols.
        ax3.plot(seed_points[0], seed_points[1], "bo")
        ax3.set(xlim=(-w, w), ylim=(-w, w))

        # Create a mask
        mask = np.zeros(U.shape, dtype=bool)
        mask[40:60, 40:60] = True
        U[:20, :20] = np.nan
        U = np.ma.array(U, mask=mask)

        ax4 = fp.add_subplot(gs=fp.gs[2:, :])
        ax4.streamplot(X, Y, U, V, color="r")
        ax4.set_title("Streamplot with Masking")

        ax4.imshow(
            ~mask,
            extent=(-w, w, -w, w),
            alpha=0.5,
            interpolation="nearest",
            cmap="gray",
            aspect="auto",
        )

        # this is the next page. Currently starts  at [0, 0]

        Y, X = np.mgrid[-w:w:100j, -w:w:100j]
        U = -1 - X ** 2 + Y
        V = 1 + X - Y ** 2

        ax3 = fp.add_subplot()
        strm = ax3.streamplot(
            X, Y, U, V, color=U, linewidth=2, cmap="autumn", start_points=seed_points.T
        )
        fp.fig.colorbar(strm.lines)
        ax3.set_title("Controlling Starting Points")

        # Displaying the starting points with blue symbols.
        ax3.plot(seed_points[0], seed_points[1], "bo")
        ax3.set(xlim=(-w, w), ylim=(-w, w))

        fp.add_page(
            nrows=1,
            ncols=1,
            orientation="landscape",
            height_ratios=[1],
            width_ratios=[1],
        )
        ax4 = fp.add_subplot()
        strm = ax4.streamplot(
            X, Y, U, V, color=U, linewidth=2, cmap="autumn", start_points=seed_points.T
        )
        fp.fig.colorbar(strm.lines)
        ax4.set_title("Controlling Starting Points")

        # Displaying the starting points with blue symbols.
        ax4.plot(seed_points[0], seed_points[1], "bo")
        ax4.set(xlim=(-w, w), ylim=(-w, w))

    print("outfile: " + outfile)
    # close the figure
    fp.close()
    print("--Done!--")


if __name__ == "__main__":
    test_main()
