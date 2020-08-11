"""
Module file that contains a FigPager class. A static function float_list_value is used for validating float lists.
Currently PDF and PGF are supported in a multipage backend.

Written by Eben Pendleton
MIT License
"""
# used to deep copy config
import copy
# used in metadata
import datetime
# used to find calling path
import inspect
import os

if os.environ.get('DISPLAY','') == '':
    import matplotlib as mpl
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

# used to draw lines on the figure
import matplotlib.lines as lines
# matplotlib import used in setting figure and axes
import matplotlib.pyplot as plt
# import package resources to get ini
import pkg_resources
# used as the multipage backend
from matplotlib.backends.backend_pdf import PdfPages
# used to set the plot layout in the figure
from matplotlib.gridspec import GridSpec

# used to validate and read in ini files
import configobj
# import the validator
from validate import Validator

# set up the base string depending if we are running Python 2 or Python 3
try:
    # check whether python knows about 'basestring'
    isinstance("aaa", basestring)
except NameError:
    # Ut doesn't (it's Python 3); use 'str' instead
    basestring = str


def float_list_value(v, minl=None, maxl=None, minv=None, maxv=None):
    """
        Validator function for float lists
    Args:
        v: input list
        minl: (optional) minimum list length allowed
        maxl: (optional) maximum list length allowed
        minv: (optional( minimum float value allowed
        maxv: (optional) maximum float value allowed

    Returns: Validated float list, i.e. [1.2, 4., 6.7]

    """

    vdt = Validator()
    is_float = vdt.functions["float"]
    is_list = vdt.functions["list"]

    return [is_float(mem, min=minv, max=maxv) for mem in is_list(v, minl, maxl)]


class FigPager:

    """ Class to use matplotlib's figure with multi and single page outputs """

    # class variables shared by all instances
    # get the path of the class
    path = os.path.abspath(__file__)

    # used to find ini files saved in the package
    page_layout_path = pkg_resources.resource_filename('figpager', 'page_layout/')

    def __init__(
        self,
        paper_size,
        nrows=None,
        ncols=None,
        layout="default",
        width_ratios=None,
        height_ratios=None,
        outfile=None,
        orientation=None,
        dpi=300,
        facecolor="w",
        edgecolor="w",
        transparent=False,
        bbox_inches=None,
        pad_inches=0.1,
        metadata=None,
        subplotstartindex=None,
        direction="left-to-right",
        overwrite=False,
        sharex=False,
        sharey=False,
    ):

        """

        Args:
            paper_size: (string) Papar size. A string defined in paper_size.ini, A0-A10, Letter, Legal, Ledger or a
            tuple of width and height
            nrows: (int) Number of rows of subplots per page.
            ncols: (int) Number of columns of subplots per page.
            layout: (string) (optional) layout name or layout filepath.
            width_ratios:  (list of ints or floats) (optional) GridSpec width ratios. Default is 1.
            height_ratios: (list of ints or floats) (optional) GridSpec height ratios. Default is 1.
            outfile: (string) (optional) out file path. If None (default) plt.show() is run.
            orientation: (string) (optional) Portrait or Landscape page orientation.
            dpi: (int) (optional) Figure dpi. Default is 300.
            facecolor: (string) (optional) Figure facecolor. Default is white.
            edgecolor: (string) (optional) Figure facecolor. Default is white.
            transparent: (boolean) (optional) Figure tranparancy. Default is False
            bbox_inches: (float) (optional) Bounding box (bbox) in inches. Only the given portion of the figure is
            saved. If 'tight', try to figure out the tight bbox of the figure. If None, use savefig.bbox
            pad_inches: (float) (optional) Amount of padding around the figure when bbox_inches is 'tight'.
            If None, use savefig.pad_inches
            metadata: (dict) (optional) Key/value pairs to store in the image metadata. The supported keys and
            defaults depend on the image format and backend:
            subplotstartindex: (list of ints) (optional) First subplot on a page row and column index.
            direction: (string) (optional) subplot creation direction. Default is left-to-right.
            overwrite: (boolean) (optional) Boolean on whether to overwrite existing output. Default is True
            sharex: share x axes in subplots. Default is False
            sharey:share y axes in subplots.Default is False
        """

        # obtain the caller path
        self.callerpath = self.get_caller_filepath()

        self.type = None
        self.outfile = None
        # Obtain the out path. Error on the outfile being a directory
        if outfile is not None:
            if os.path.isdir(outfile):
                raise IOError("This is a directory. Please provide a file path.")

            # test if outfile exists already and raise an error if it does
            if os.path.isfile(outfile):
                if overwrite:
                    os.remove(outfile)
                else:
                    data = input(
                        "The output file already exists. "
                        + "Would you like to overwrite? [y/n] "
                    )

                    if data.lower() == "y":
                        os.remove(outfile)
                    else:
                        raise IOError(
                            "Output file already exists and user chose not to overwrite."
                        )
                # hold file type
                self.type = os.path.splitext(outfile)[1][1:]

            # hold outfile full path
            self.outfile = outfile



        # hold multipage indicator
        self.multipage = False
        if self.type in ["pdf", "pgf"]:

            # Create the PdfPages object to which we will save the pages:
            self.pdf = PdfPages(self.outfile)
            self.multipage = True

        # initialize layout containers
        # to hold layout file path
        self.layout_path = None
        # to hold the layout name
        self.layout = None

        # read in the layout we are using and set layout and layout path
        self._read_layout(layout)
        # set up config
        self.config = None

        # determine the papersize from inputs
        # if its a string rather than a tuple then read in the value a0, etc)
        if isinstance(paper_size, basestring):
            cfg = """
            [paper_sizes]
            [[__many__]]
            width_mm=integer
            height_mm=integer
            width_in=float
            height_in=float
            """
            # formst the config above
            spec = cfg.split("\n")

            # read in the ini file of paper sizes
            config = configobj.ConfigObj(
                os.path.join(self.page_layout_path, "paper_sizes.ini"),
                configspec=spec,
            )

            # validate against the config above
            vdt = Validator()
            config.validate(vdt)

            # save the paper size config
            self.paper_size_config = copy.deepcopy(config)

            # set up and store paper / page attributes
            self.pagewidth_inch = None
            self.pageheight_inch = None

            self.orientation = orientation
            self.paper_size = paper_size

            # update the orientation based on paper size
            self._set_paper_size_orientation()

        # set up the figure parameters from init
        self.nrows = nrows
        self.ncols = ncols
        self.height_ratios = height_ratios
        self.width_ratios = width_ratios
        self.sharex = sharex
        self.sharey = sharey

        # figure attributes
        self.fig = None
        self.dpi = dpi
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.transparent = transparent
        self.bbox_inches = bbox_inches
        self.pad_inches = pad_inches
        self.metadata = metadata

        # save current filename as possible next filename base if not multipage
        self.new_fname = self.outfile
        # list to append multiple filenames
        self.newfnameall = []

        # saves current figure count for use in non multipage
        self.fignumber = 1

        # set up margin frame and margins
        self.figure_unit = None
        self.figure_unit_conversion = 1
        self.marginframe = None
        self.constrained_layout = None
        self.leftmargin = None
        self.rightmargin = None
        self.topmargin = None
        self.bottommargin = None
        self.marginpad = None

        self.framewidth = None
        self.frameheight = None

        # set up the source path attributes
        # the source path is a path to the calling script
        self.source_path = None
        self.source_path_position = None
        self.source_path_fontcolor = None
        self.source_path_fontsize = None

        # update from layout
        self._update_from_layout()

        # set the inital subgraphic index
        self.subplotstartindex = subplotstartindex
        self.currentsubplotindex = subplotstartindex
        self.direction = direction

        # transform storage
        self.transform = None

        # update from layout
        self._update_from_layout()
        # draw the initial page
        self.fig, self.ax, self.gs, self.transform = self.draw_page()

    def __enter__(self):
        """ Return self on entry """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Close the figure on exit"""

        self.close()
        return True

    def get_caller_filepath(self):

        """
        Get the caller absolute file path.
        Reference:  https://stackoverflow.com/a/55469882
        Get the caller's stack frame and extract its file path
        """

        frame_info = inspect.stack()[-1]
        # in python 3.5+, you can use frame_info.filename
        filepath = frame_info[1]
        # drop the reference to the stack frame to avoid reference cycles
        del frame_info

        # make the path absolute
        filepath = os.path.abspath(filepath)
        return filepath

    def _read_layout(self, layout):
        """
        Reads the layout path and determines if its within the package or an external path
        This sets the self.layout and self.layout_path

        Args:
            layout: layout name if under figpager.page_layout or file path

        Returns: None

        """

        if os.path.isfile(os.path.join(self.page_layout_path, layout + ".ini")):
            self.layout_path = os.path.join(self.page_layout_path, layout + ".ini")
            self.layout = layout

        elif os.path.isfile(layout):
            self.layout_path = layout
            self.layout = os.path.splitext(os.path.basename(layout))[0]

        elif layout is None:
            self.layout = layout
            self.layout_path = None
        else:
            raise ValueError("Not a valid internal layout or layout file path.")

    def _set_paper_size_orientation(self):

        """
        Obtain the height and width of the page based on the paper size
        Correct if the orientation has them flipped
        Returns: None

        """

        self.pagewidth_inch = self.paper_size_config["paper_sizes"][
            self.paper_size.lower()
        ]["width_in"]
        self.pageheight_inch = self.paper_size_config["paper_sizes"][
            self.paper_size.lower()
        ]["height_in"]

        if self.paper_size_config["paper_sizes"][self.paper_size.lower()] is None:
            raise ValueError("paper size not found")

        if isinstance(self.paper_size, tuple):
            self.pagewidth_inch = self.paper_size[0]
            self.pageheight_inch = self.paper_size[1]

        if self.orientation is None:
            if self.pageheight_inch > self.pagewidth_inch:
                self.orientation = "portrait"
            else:
                self.orientation = "landscape"
        else:
            assert self.orientation.lower() in ["portrait", "landscape"], (
                "Unknown orientation: " + self.orientation
            )

        # check the orientation against the height and width. Flip if needed
        if self.orientation == "portrait":
            if self.pageheight_inch < self.pagewidth_inch:
                h = self.pageheight_inch
                self.pageheight_inch = self.pagewidth_inch
                self.pagewidth_inch = h

        if self.orientation == "landscape":
            if self.pageheight_inch > self.pagewidth_inch:
                h = self.pageheight_inch
                self.pageheight_inch = self.pagewidth_inch
                self.pagewidth_inch = h

    def _process_config(self, file):
        """
        Handles configuration file processing. Add keys and values to validdict as needed.
        cfg = """

        # read the supplied config file and set up the config spec using validDict. Error if key is not found.
        with open(file, "r") as myfile:

            validdict = {
                "figure_unit": "option('inch', 'mm', default='inch')",
                "constrained_layout": "boolean",
                "source_path": "boolean",
                "source_path_position": "float_list_value",
                "source_path_fontcolor": "string",
                "source_path_fontsize": "float",
                "margin_frame": "boolean",
                "left_margin": "float(min=0)",
                "right_margin": "float(min=0)",
                "top_margin": "float(min=0)",
                "bottom_margin": "float(min=0)",
                "margin_pad": "float",
                "framecolor": "string",
                "framelinewidth": "float",
                "box_frame": "boolean",
                "box_label": "string",
                "box_adjust_margin": "boolean",
                "box_position": "float_list_value",
                "box_height": "float",
                "box_width": "float",
                "text": "string",
                "text_position": "float_list_value",
                "text_position_offset": "float_list_value",
                "horizontalalignment": "string",
                "fontcolor": "string",
                "fontsize": "float",
                "fontstyle": "string",
                "rotation": "integer",
                "line_position_start": "float_list_value",
                "line_position_end": "float_list_value",
                "line_position_offset": "float_list_value",
                "line_min": "float",
                "line_max": "float",
                "line_length": "string",
                "line_width": "float",
                "line_color": "string",
                "linestyle": "string",
                "image_path": "string",
                "image_position": "float_list_value",
                "image_position_offset": "float_list_value",
            }

            data = myfile.read()

            # handle some Python 2 / Python 3 line endings differences. Present on macOS at least.
            data = data.replace("\r", "")
            # split line breaks

            tmp = data.replace("\n", "$")
            tmp = tmp.split("$")
            tmp = [t.strip() for t in tmp if t != ""]
            cfg = ""
            block_comment = False
            for t in tmp:
                t = t.strip().strip("'")
                t = t.replace("'", "")

                # block comment
                if t[0:3] == '"""':
                    block_comment = not block_comment
                if block_comment:
                    continue

                # if not a comment
                if t[0] not in ["#", "["]:
                    if "=" in t:
                        try:
                            txt = validdict[t.split("=")[0].strip()]
                            cfg = cfg + "\n" + t.split("=")[0].strip() + " = " + txt
                        except KeyError:
                            raise KeyError(
                                "Key + " + t.split("=")[0].strip() + " not found"
                            )

                # if the line can not be split with '=' then treat it as a whole line
                # and add a line break and move to the next line
                else:
                    cfg = cfg + "\n" + t

        # return the read and processed format
        return cfg

    def _parse_block_comments(self, file):

        """
        Convert block comments """ """ to # lines
        Args:
            file: configuration file

        Returns: a list of each line in the configuration lie with libes between block comments commented as #

        """
        # read the supplied config file add comment to a StringIO object
        stream = []
        block_comment = False
        with open(file, "r") as file:
            for line in file:
                # block comment

                if line == '"""\n':
                    block_comment = not block_comment
                    line = "#" + line
                elif block_comment:
                    line = "#" + line

                stream.append(line)

        return stream

    def _parse_option(self, section, subsection, option):

        """
        Parse a given config option given the file's section, subsection and option.
        Return None if option is not found
        Args:
            section: config file section. [example]
            subsection: config file subsection. [[example]]
            option: config file option. example=True

        Returns: option value or None

        """

        try:
            return self.config[section][subsection][option]
        except KeyError:
            try:
                return self.config[section][subsection][self.paper_size.title()][
                    self.orientation.title()
                ][option]
            except KeyError:
                return None

    def _update_from_layout(self):

        """
        Updates FogPager instance with given config file
        """

        if self.layout_path is not None:
            # process configuration
            cfg = self._process_config(self.layout_path)

            spec = cfg.split("\n")

            file = self._parse_block_comments(self.layout_path)

            vdt = Validator()
            vdt.functions["float_list_value"] = float_list_value
            config = configobj.ConfigObj(file, configspec=spec)
            config.validate(vdt)

            # use self.config.sections() to see the sections
            # use self.config.get('SectionName', 'option') to get the option value
            self.config = copy.deepcopy(config)

            if not self.config:
                raise ValueError("Figure Layout not found: " + self.layout_path)

            self.constrained_layout = self._parse_option(
                "Layout", "Margin", "constrained_layout"
            )

            self.figure_unit = self._parse_option("Layout", "Margin", "figure_unit")
            if self.figure_unit == "mm":
                # mm to inches conversion
                self.figure_unit_conversion = 0.0393701
                self.pagewidth_inch = self.pagewidth_inch * self.figure_unit_conversion
                self.pageheight_inch = (
                    self.pageheight_inch * self.figure_unit_conversion
                )

            self.marginframe = self._parse_option("Layout", "Margin", "margin_frame")
            if self.marginframe:
                self.constrained_layout = False
                self.leftmargin = (
                    self._parse_option("Layout", "Margin", "left_margin")
                    * self.figure_unit_conversion
                )
                self.rightmargin = (
                    self._parse_option("Layout", "Margin", "right_margin")
                    * self.figure_unit_conversion
                )
                self.topmargin = (
                    self._parse_option("Layout", "Margin", "top_margin")
                    * self.figure_unit_conversion
                )
                self.bottommargin = (
                    self._parse_option("Layout", "Margin", "bottom_margin")
                    * self.figure_unit_conversion
                )
                self.marginpad = (
                    self._parse_option("Layout", "Margin", "margin_pad")
                    * self.figure_unit_conversion
                )

                self.framewidth = (
                    self.pagewidth_inch - self.leftmargin - self.rightmargin
                )
                self.frameheight = (
                    self.pageheight_inch - self.topmargin - self.bottommargin
                )
            else:
                self.leftmargin = 0
                self.rightmargin = 0
                self.topmargin = 0
                self.bottommargin = 0
                self.marginpad = 0
                self.framewidth = self.pagewidth_inch
                self.frameheight = self.pageheight_inch


            self.source_path = self._parse_option("Layout", "Margin", "source_path")
            self.source_path_position = [
                v * self.figure_unit_conversion
                for v in self._parse_option("Layout", "Margin", "source_path_position")
            ]
            self.source_path_fontcolor = self._parse_option(
                "Layout", "Margin", "source_path_fontcolor"
            )
            self.source_path_fontsize = self._parse_option(
                "Layout", "Margin", "source_path_fontsize"
            )

            # read text
            self.configtext = self.config["Text"]

    def _text_from_label(self, section, label, txt):

        """
        Find label and write text at label position with label font characteristics
        Args:
            section: Configuration file text section
            label:  Configuration file text label
            txt: text to display at given label parameters

        Returns: None

        """

        xcoord = self._parse_option(section, label, "text_position")[0]
        ycoord = self._parse_option(section, label, "text_position")[1]
        if self._parse_option(section, label, "text_position")[0] == "right_margin":
            xcoord = self.pagewidth_inch - self.rightmargin

        if self._parse_option(section, label, "text_position")[0] == "left_margin":
            xcoord = self.leftmargin

        if self._parse_option(section, label, "text_position")[1] == "top_margin":
            ycoord = self.pageheight_inch - self.topmargin

        if self._parse_option(section, label, "text_position")[1] == "bottom_margin":
            ycoord = self.bottommargin

        xcoord = float(xcoord)
        ycoord = float(ycoord)

        if self._parse_option(section, label, "text_position_offset") is not None:
            xcoord = xcoord + float(
                self._parse_option(section, label, "text_position_offset")[0]
            )
            ycoord = ycoord + float(
                self._parse_option(section, label, "text_position_offset")[1]
            )

        fontstyle = self._parse_option(section, label, "fontstyle")

        if fontstyle is None:
            fontstyle = "normal"

        rotation = self._parse_option(section, label, "rotation")
        if rotation is None:
            rotation = 0

        plt.figtext(
            xcoord / self.pagewidth_inch,
            ycoord / self.pageheight_inch,
            txt,
            horizontalalignment=self._parse_option(
                section, label, "horizontalalignment"
            ),
            color=self._parse_option(section, label, "fontcolor"),
            fontsize=self._parse_option(section, label, "fontsize"),
            transform=self.transform,
            fontstyle=fontstyle,
            rotation=rotation,
        )

    def _box_from_label(self, label):

        """
        Draw a box based on a given label from a configuration file

        Args:
            label: Configuration file box label

        Returns: x, y coordinates and box height

        """

        if self.config["Boxes"][label]["box_frame"]:
            xcoord = self.config["Boxes"][label]["box_position"][0]
            ycoord = self.config["Boxes"][label]["box_position"][1]
            width = self.config["Boxes"][label]["box_width"]
            height = self.config["Boxes"][label]["box_height"]

            if height in ["left_margin", "right_margin"]:
                height = self.frameheight

            if self.config["Boxes"][label]["box_position"][0] == "right_margin":
                xcoord = self.pagewidth_inch - self.rightmargin + width

            elif self.config["Boxes"][label]["box_position"][0] == "left_margin":
                xcoord = self.leftmargin

            else:
                xcoord = float(xcoord)

            if self.config["Boxes"][label]["box_position"][1] == "top_margin":
                ycoord = self.pageheight_inch - self.topmargin
                # update the bottom margin as needed
                if ycoord + height < self.pageheight_inch - self.topmargin:

                    self.frameheight = self.frameheight + height
                    if height < 0:
                        ycoord = ycoord + height
                        self.topmargin = self.topmargin + abs(height)

            elif self.config["Boxes"][label]["box_position"][1] == "bottom_margin":
                ycoord = self.bottommargin
                # update the bottom margin as needed
                if ycoord + height > self.bottommargin:
                    if width == "frame_width":
                        self.bottommargin = ycoord + height
                        self.frameheight = self.frameheight - height
            else:
                ycoord = float(ycoord)

            if width == "frame_width":
                width = self.framewidth

            if width != self.framewidth:
                if width > 0:
                    # update the left margin as needed
                    if xcoord + width > self.leftmargin:
                        self.leftmargin = xcoord + width
                        # update the frame width

                        if width < self.framewidth:
                            self.framewidth = self.framewidth - width
                else:
                    width = abs(width)
                    self.rightmargin = self.rightmargin + width
                    self.framewidth = self.framewidth - width

            xcoord = xcoord / self.pagewidth_inch
            ycoord = ycoord / self.pageheight_inch
            width = width / self.pagewidth_inch
            height = height / self.pageheight_inch
            if height < 0:
                height = abs(height)

            self.fig.add_axes([xcoord, ycoord, width, height])

            # this turns off the ticks and labels of the margin box
            plt.tick_params(
                axis="both",  # changes apply to both
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
                labelleft=False,
                left=False,
                right=False,
            )
            return xcoord, ycoord, self.config["Boxes"][label]["box_height"]

    def _line_from_label(self, label):

        """
        Draw a line based on a given label from a configuration file

        Args:
            label: configuration file line label

        Returns: None

        """
        pos = self._parse_option("Lines", label, "line_position_start")
        pos2 = self._parse_option("Lines", label, "line_position_end")

        if self._parse_option("Lines", label, "image_position_offset") is not None:
            pos[0] = pos[0] + float(
                self._parse_option("Images", label, "image_position_offset")[0]
            )
            pos[1] = pos[1] + float(
                self._parse_option("Images", label, "image_position_offset")[1]
            )

            pos2[0] = pos2[0] + float(
                self._parse_option("Images", label, "image_position_offset")[0]
            )
            pos2[1] = pos2[1] + float(
                self._parse_option("Images", label, "image_position_offset")[1]
            )


        l1 = lines.Line2D(
            [pos[0] / self.pagewidth_inch, pos2[0] / self.pagewidth_inch],
            [pos[1] / self.pageheight_inch, pos2[1] / self.pageheight_inch],
            transform=self.transform,
            figure=self.fig,
            color=self._parse_option("Lines", label, "line_color"),
            linestyle=self._parse_option("Lines", label, "linestyle"),
            linewidth=self._parse_option("Lines", label, "line_width"),
        )

        self.fig.lines.extend([l1])

    def _image_from_label(self, label):

        """
        Draw an image based on a given label from a configuration file

        Args:
            label: configuration file image label

        Returns:

        """
        pos = self._parse_option("Images", label, "image_position")
        fname = self._parse_option("Images", label, "image_path")

        if self._parse_option("Images", label, "image_position_offset") is not None:
            pos[0] = pos[0] + float(
                self._parse_option("Images", label, "image_position_offset")[0]
            )
            pos[1] = pos[1] + float(
                self._parse_option("Images", label, "image_position_offset")[1]
            )

        if fname:
            filename, file_extension = os.path.splitext(fname)
            img = plt.imread(fname, format=file_extension)
            width1 = img.shape[0]
            height1 = img.shape[1]

            width, height = self.fig.get_size_inches() * self.fig.get_dpi()
            # We're specifying the position and size in figure coordinates, so the image
            # will shrink/grow as the figure is resized.
            # zorder = 1 places the images on top
            ax = self.fig.add_axes(
                [
                    pos[0] / self.pagewidth_inch,
                    pos[1] / self.pageheight_inch,
                    width1 / width,
                    height1 / height,
                ],
                anchor="SW",zorder=1,
            )
            ax.imshow(img)
            ax.axis("off")

    def text_from_label(self, label, txt):
        """
               Public function to find label and write text at label position with label font characteristics.
               Assumes label is in text section
               Args:
                   section: Configuration file text section
                   label:  Configuration file text label
                   txt: text to display at given label parameters

               Returns: None

        """
        return self._text_from_label("Text", label, txt)

    def draw_page(self):
        """
        Draw the current page

        Returns: fig; figure instance, ax; axes instances, gs; GridSpec, self.transform; Figure Transform

        """

        plt.clf()

        # if there's a margin frame set the constrained layout to False
        if self.marginframe:
            self.constrained_layout = False

        # set up the figure
        fig, ax = plt.subplots(
            constrained_layout=self.constrained_layout,
            figsize=(self.pagewidth_inch, self.pageheight_inch),
            squeeze=False, sharex=self.sharex, sharey=self.sharey,
        )

        # set the patch here
        fig.patch.set_visible(not self.transparent)
        # save the transform
        self.transform = fig.transFigure

        # save the fig
        self.fig = fig

        # this turns off the ticks and labeks of the box
        plt.tick_params(
            axis="both",  # changes apply to both
            which="both",  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False,
            labelleft=False,
            left=False,
            right=False,
        )
        [axi.set_axis_off() for axi in ax.ravel()]

        gs = GridSpec(
            self.nrows,
            self.ncols,
            width_ratios=self.width_ratios,
            height_ratios=self.height_ratios,
            figure=fig,
        )

        # add the path if set
        if self.source_path:
            # get the x, y positions
            pos = self.source_path_position

            plt.figtext(
                pos[0] / self.pagewidth_inch,
                pos[1] / self.pageheight_inch,
                self.callerpath,
                color=self.source_path_fontcolor,
                fontsize=self._parse_option("Layout", "Margin", "source_path_fontsize"),
                transform=self.transform,
            )

        # add the margin frame if set
        if self.marginframe:

            # add any layout set boxes here:
            if any(self.config["Boxes"].keys()):
                for k in self.config["Boxes"].keys():
                    self._box_from_label(k)

            # margin box
            # read in the margins and adjust padding
            # where a list [x0, y0, width, height]
            # denoting the lower left point of the new axes in figure coodinates
            # (x0,y0) and its width and height
            # In example, ax = fig.add_axes([0,0,1,1])
            # places a figure in the canvas that is exactly as large as the canvas itself.
            width = (
                self.pagewidth_inch - self.leftmargin - self.rightmargin
            ) / self.pagewidth_inch
            height = (
                self.pageheight_inch - self.topmargin - self.bottommargin
            ) / self.pageheight_inch

            with plt.rc_context(
                {
                    "axes.edgecolor": self._parse_option(
                        "Layout", "Margin", "framecolor"
                    ),
                    "figure.facecolor": "white",
                }
            ):
                ax = fig.add_axes(
                    [
                        self.leftmargin / self.pagewidth_inch,
                        self.bottommargin / self.pageheight_inch,
                        width,
                        height,
                    ]
                )
                ax.patch.set_edgecolor(
                    self._parse_option("Layout", "Margin", "framecolor")
                )
                ax.patch.set_linewidth(
                    self._parse_option("Layout", "Margin", "framelinewidth")
                )

            # this turns off the ticks and labeks of the margin box
            plt.tick_params(
                axis="both",  # changes apply to both
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
                labelleft=False,
                left=False,
                right=False,
            )

            # fig.add_artist(plt.gca())
            # ax.add_artist(plt.gca())

            # these are fractions of the figure. Here everything the is same unit
            plt.subplots_adjust(
                left=(self.leftmargin + self.marginpad) / self.pagewidth_inch,
                right=(self.framewidth + self.leftmargin - self.marginpad)
                / self.pagewidth_inch,
                bottom=(self.bottommargin + self.marginpad) / self.pageheight_inch,
                top=(self.frameheight + self.bottommargin - self.marginpad)
                / self.pageheight_inch,
            )

        # This resets the margins and other parameters to layout
        if self.marginframe:
            self._update_from_layout()

        # add any layout set text here
        for k in self.config["Text"].keys():
            if self._parse_option("Text", k, "text") is not None:
                self._text_from_label("Text", k, self._parse_option("Text", k, "text"))

        # add any layout set images here
        for k in self.config["Images"].keys():
            self._image_from_label(k)

        # add any lines here
        for k in self.config["Lines"].keys():
            self._line_from_label(k)

        # add any layout set watermarks here
        for k in self.config["Watermark"].keys():
            if self._parse_option("Watermark", k, "text") is not None:
                self._text_from_label(
                    "Watermark", k, self._parse_option("Watermark", k, "text")
                )

        return fig, ax, gs, self.transform

    def add_subplot(self, direction="left-to-right", pos=None, gs=None, **kwargs):
        """

        Args:
            direction: (optional) subplot advancing direction. left-to-right (default) or Top-to-bottom is supported
            pos: (optional) gridSpec position keyword in the form of [row,column]
            gs: (optional) GridSpec specification for more advanced positions
            **kwargs: (optional) any additional add_subplot keywords

        Returns: fig.add_subplot()

        """
        if direction:
            self.direction = direction

        if pos is None:
            pos = self.currentsubplotindex

            if self.direction == "left-to-right":
                if self.subplotstartindex is None:
                    pos = [0, 0]
                    self.subplotstartindex = [0, 0]
                else:
                    # pos = self.subplotstartindex
                    # try to add a column
                    if pos[1] < self.ncols - 1:
                        # use the existing row and add a column
                        pos = [pos[0], pos[1] + 1]

                    elif pos[0] < self.nrows - 1:
                        # add the row and reset the columns
                        pos = [pos[0] + 1, 0]

                    else:
                        # reset the starting position
                        pos = self.subplotstartindex
                        self.fig, self.ax, self.gs, self.transform = self.add_page(
                            subplotstartindex=self.subplotstartindex
                        )

            if self.direction == "top-to-bottom":
                if self.subplotstartindex is None:
                    pos = [0, 0]
                    self.subplotstartindex = [0, 0]
                else:
                    # pos = self.subplotstartindex
                    # try to add a row
                    if pos[0] < self.nrows - 1:
                        # add the row and use the existing columns
                        pos = [pos[0] + 1, pos[1]]

                    # try to add a column
                    elif pos[1] < self.ncols - 1:

                        # add the column and reset the rows
                        pos = [0, pos[1] + 1]

                    else:
                        # zero the starting position
                        pos = self.subplotstartindex
                        self.fig, self.ax, self.gs, self.transform = self.add_page(
                            subplotstartindex=self.subplotstartindex
                        )
        else:
            self.subplotstartindex = pos

        self.currentsubplotindex = pos

        if gs is None:
            return self.fig.add_subplot(
                self.gs[pos[0], pos[1]],
                label="({},{})".format(pos[0], pos[1]),
                **kwargs
            )
        else:
            self.currentsubplotindex = [
                gs.get_topmost_subplotspec().get_gridspec().get_geometry()[0],
                gs.get_topmost_subplotspec().get_gridspec().get_geometry()[1],
            ]

            return self.fig.add_subplot(
                gs,
                label="({},{})".format(
                    self.currentsubplotindex[0], self.currentsubplotindex[1]
                ),
                **kwargs
            )

    def add_page(
        self,
        paper_size=None,
        nrows=None,
        ncols=None,
        layout=None,
        width_ratios=None,
        height_ratios=None,
        outfile=None,
        orientation=None,
        dpi=None,
        facecolor=None,
        edgecolor=None,
        transparent=None,
        bbox_inches=None,
        pad_inches=None,
        metadata=None,
        subplotstartindex=None,
        direction="left-to-right",
    ):

        """

        Add a new page

        Args:
            paper_size: (string) Papar size. A string defined in paper_size.ini, A0-A10, Letter, Legal, Ledger or a
            tuple of width and height
            nrows: (int) Number of rows of subplots per page.
            ncols: (int) Number of columns of subplots per page.
            layout: (string) (optional) layout name or layout filepath.
            width_ratios:  (list of ints or floats) (optional) GridSpec width ratios. Default is 1.
            height_ratios: (list of ints or floats) (optional) GridSpec height ratios. Default is 1.
            outfile: (string) (optional) out file path. If None (default) plt.show() is run.
            orientation: (string) (optional) Portrait or Landscape page orientation.
            dpi: (int) (optional) Figure dpi. Default is 300.
            facecolor: (string) (optional) Figure facecolor. Default is white.
            edgecolor: (string) (optional) Figure facecolor. Default is white.
            transparent: (boolean) (optional) Figure tranparancy. Default is False
            bbox_inches: (float) (optional) Bounding box (bbox) in inches. Only the given portion of the figure is
            saved. If 'tight', try to figure out the tight bbox of the figure. If None, use savefig.bbox
            pad_inches: (float) (optional) Amount of padding around the figure when bbox_inches is 'tight'.
            If None, use savefig.pad_inches
            metadata: (dict) (optional) Key/value pairs to store in the image metadata. The supported keys and
            defaults depend on the image format and backend:
            subplotstartindex: (list of ints) (optional) First subplot on a page row and column index.
            direction: (string) (optional) subplot creation direction. Default is Left-to-right.

        Returns: fig; figure instance, ax; axes instances, gs; GridSpec, self.transform; Figure Transform

        """

        if self.type in ["pdf", "pgf"]:
            try:
                self.pdf.savefig(
                    self.fig,
                    dpi=self.dpi,
                    facecolor=self.facecolor,
                    edgecolor=self.edgecolor,
                    orientation=self.orientation,
                    transparent=self.transparent,
                    bbox_inches=self.bbox_inches,
                    pad_inches=self.pad_inches,
                    metadata=self.metadata,
                )
            except AttributeError as a:
                if str(a) == "'NoneType' object has no attribute 'endStream'":
                    raise AttributeError("Cannot add a new page to a closed pdf file.")
        elif self.type is not None:
            # number 02, 03 etc '{:02}'.format(1)
            plt.savefig(
                self.new_fname,
                dpi=self.dpi,
                facecolor=self.facecolor,
                edgecolor=self.edgecolor,
                orientation=self.orientation,
                transparent=self.transparent,
                bbox_inches=self.bbox_inches,
                pad_inches=self.pad_inches,
                metadata=self.metadata,
            )
            # append multiple filenames
            self.newfnameall.append(self.new_fname)

            filename, file_extension = os.path.splitext(self.outfile)
            self.fignumber = self.fignumber + 1
            self.new_fname = "{}_{}{}".format(
                filename, "{:02}".format(self.fignumber), file_extension
            )
        else:
            plt.show()
        plt.close(self.fig)

        if paper_size is not None:
            self.paper_size = paper_size

        if nrows is not None:
            self.nrows = nrows

        if ncols is not None:
            self.ncols = ncols

        if width_ratios is not None or height_ratios is not None:
            self.width_ratios = width_ratios
            self.height_ratios = height_ratios

        if outfile is not None:
            if not self.multipage:
                self.outfile = outfile
            else:
                raise ValueError(
                    "outfile can't be changed per page in a multipage document."
                )

        if orientation is not None:
            self.orientation = orientation
            self._set_paper_size_orientation()
            # update the margin frame
            self.framewidth = self.pagewidth_inch - self.leftmargin - self.rightmargin
            self.frameheight = self.pageheight_inch - self.topmargin - self.bottommargin

        if dpi is not None:
            self.dpi = dpi

        if facecolor is not None:
            self.facecolor = facecolor

        if edgecolor is not None:
            self.edgecolor = edgecolor

        if transparent is not None:
            self.transparent = transparent

        if bbox_inches is not None:
            self.bbox_inches = bbox_inches

        if pad_inches is not None:
            self.pad_inches = pad_inches

        if metadata is not None:
            self.metadata = metadata

        if subplotstartindex == [0, 0] or subplotstartindex is None:
            self.subplotstartindex = None
        else:
            self.subplotstartindex = subplotstartindex

        self.direction = direction

        if layout is not None:
            self.layout = layout
            self._read_layout(layout)
            # update from layout
            self._update_from_layout()

        self.fig, self.ax, self.gs, self.transform = self.draw_page()

        return self.fig, self.ax, self.gs, self.transform

    def close(self):
        """ close the current figure by saving or viewing. Uses the
        figure attributes in self

        Returns: No return on figure close and empty return on plt.show() close

        """

        if self.outfile is not None:
            if self.type not in ["pdf", "pgf"]:
                plt.savefig(
                    self.new_fname,
                    dpi=self.dpi,
                    facecolor=self.facecolor,
                    edgecolor=self.edgecolor,
                    orientation=self.orientation,
                    transparent=self.transparent,
                    bbox_inches=self.bbox_inches,
                    pad_inches=self.pad_inches,
                    metadata=self.metadata,
                )
                self.newfnameall.append(self.new_fname)

                # update the outfile name if needed
                if self.newfnameall:
                    self.outfile = '\n'.join(self.newfnameall)
            else:
                self.pdf.savefig(
                    self.fig,
                    dpi=self.dpi,
                    facecolor=self.facecolor,
                    edgecolor=self.edgecolor,
                    orientation=self.orientation,
                    transparent=self.transparent,
                    bbox_inches=self.bbox_inches,
                    pad_inches=self.pad_inches,
                    metadata=self.metadata,
                )
                # We can also set the file's metadata via the PdfPages object:
                d = self.pdf.infodict()
                # Example
                # d["Title"] = "Multipage PDF Example"
                # d["Author"] = "Author Name"
                # d["Subject"] = "How to create a multipage pdf file and set its metadata"
                # d["Keywords"] = "PdfPages multipage keywords author title subject"
                d["CreationDate"] = datetime.datetime.today()
                d["ModDate"] = datetime.datetime.today()

                # Remember to close the object - otherwise the file will not be usable
                self.pdf.close()


        else:
            plt.show()
            plt.close(self.fig)
            return
