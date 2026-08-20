"""Collections of various bits of code that should not be included during compilation"""

import os
import re
import sys

from personal_python_ast_optimizer.config import TokensToFold
from personal_python_ast_optimizer.regex.replace import RegexReplacement
from personal_python_ast_optimizer.typing import FoldableConstant
from PIL.AvifImagePlugin import DECODE_CODEC_CHOICE
from PIL.DdsImagePlugin import DDS_MAGIC
from PIL.GifImagePlugin import _FORCE_OPTIMIZE
from PIL.GimpGradientFile import EPSILON
from PIL.Image import WARN_POSSIBLE_FORMATS
from PIL.ImageFile import MAXBLOCK
from PIL.ImageFont import MAX_STRING_LENGTH

from compile_utils.constants import IMAGE_VIEWER_NAME
from image_viewer.constants import TEXT_RGB
from image_viewer.image.image_io import (
    DEFAULT_DURATION_MS,
    MAX_ZOOM_RATIO_TO_SCREEN,
    ZOOM_AMOUNT,
)
from image_viewer.image.resizer import JPEG_MAX_DIMENSION
from image_viewer.ui.rename_entry import _ERROR_COLOR, _MAX_ENTRY_SIZE

modules_to_skip: list[str] = [
    "argparse",
    "bz2",
    "csv",
    "email",
    "email.message",
    "email.parser",
    "lzma",
    "PIL.__main__",
    "PIL._deprecate",
    "PIL._typing",
    "PIL._version",
    "PIL.BdfFontFile",
    "PIL.BlpImagePlugin",
    "PIL.BmpImagePlugin",
    "PIL.BufrStubImagePlugin",
    "PIL.ContainerIO",
    "PIL.CurImagePlugin",
    "PIL.DcxImagePlugin",
    "PIL.EpsImagePlugin",
    "PIL.FitsImagePlugin",
    "PIL.FliImagePlugin",
    "PIL.FpxImagePlugin",
    "PIL.FtexImagePlugin",
    "PIL.GdImageFile",
    "PIL.GbrImagePlugin",
    "PIL.GribStubImagePlugin",
    "PIL.Hdf5StubImagePlugin",
    "PIL.IcnsImagePlugin",
    "PIL.IcoImagePlugin",
    "PIL.ImageGrab",
    "PIL.ImImagePlugin",
    "PIL.ImtImagePlugin",
    "PIL.IptcImagePlugin",
    "PIL.Jpeg2KImagePlugin",
    "PIL.McIdasImagePlugin",
    "PIL.MicImagePlugin",
    "PIL.MpegImagePlugin",
    "PIL.MpoImagePlugin",
    "PIL.MspImagePlugin",
    "PIL.PalmImagePlugin",
    "PIL.PcdImagePlugin",
    "PIL.PcfFontFile",
    "PIL.PcxImagePlugin",
    "PIL.PdfImagePlugin",
    "PIL.PdfParser",
    "PIL.PixarImagePlugin",
    "PIL.PpmImagePlugin",
    "PIL.PsdImagePlugin",
    "PIL.PSDraw",
    "PIL.QoiImagePlugin",
    "PIL.SgiImagePlugin",
    "PIL.SpiderImagePlugin",
    "PIL.SunImagePlugin",
    "PIL.TgaImagePlugin",
    "PIL.TiffImagePlugin",
    "PIL.WalImageFile",
    "PIL.WmfImagePlugin",
    "PIL.XbmImagePlugin",
    "PIL.XpmImagePlugin",
    "PIL.XVThumbImagePlugin",
    "PIL.FontFile",
    "PIL.ImageCms",
    "PIL.ImageDraw2",
    "PIL.ImageEnhance",
    "PIL.ImageFilter",
    "PIL.ImageMorph",
    "PIL.ImagePath",
    "PIL.ImageQt",
    "PIL.ImageShow",
    "PIL.ImageStat",
    "PIL.ImageTransform",
    "PIL.ImageWin",
    "PIL.TarIO",
    "PIL.TiffTags",
    "PIL.features",
    "PIL.report",
    "py_compile",
    "pydoc",
    "select",
    "statistics",
]


if os.name == "nt":
    modules_to_skip += ["PIL._tkinter_finder", "selectors"]
else:
    # TODO: Skip everything but plat other?
    modules_to_skip += ["send2trash.mac", "send2trash.plat_gio", "send2trash.win"]

# Module independent skips

decorators_to_always_skip: set[str] = {
    "abc.abstractmethod",
    "abstractmethod",
    "override",
}
functions_to_always_skip: set[str] = {"logger.debug", "warnings.warn"}

# Module dependent skips

assignments_to_skip: dict[str, set[str]] = {
    "PIL.AvifImagePlugin": {"format_description"},
    "PIL.DdsImagePlugin": {"format_description"},
    "PIL.GifImagePlugin": {"_Palette", "format_description"},
    "PIL.Image": {
        "DecoderInput",
        "MIME",
        "_ENDIAN",
        "_ExifBase",
        "_fromarray_typemap",
        "logger",
    },
    "PIL.ImageDraw": {"Outline"},
    "PIL.ImageFile": {"logger"},
    "PIL.ImagePalette": {"tostring"},
    "PIL.JpegImagePlugin": {"format_description"},
    "PIL.PngImagePlugin": {"format_description", "logger"},
    "PIL.WebPImagePlugin": {"format_description"},
}

if os.name == "nt":
    assignments_to_skip["PIL.AvifImagePlugin"] = {"DEFAULT_MAX_THREADS"}

classes_to_skip: dict[str, set[str]] = {
    "PIL.Image": {
        "Exif",
        "SupportsArrayInterface",
        "SupportsArrowArrayInterface",
        "SupportsGetData",
    },
    "PIL.ImageFile": {"Parser", "PyEncoder", "StubHandler", "StubImageFile"},
    "PIL.ImageFont": {"Axis", "TransposedFont"},
    "PIL.ImageOps": {"SupportsGetMesh"},
    "PIL.ImageTk": {"BitmapImage"},
    "PIL.PngImagePlugin": {"PngInfo"},
}


functions_to_skip: dict[str, set[str]] = {
    "PIL._binary": {"i8", "si16be", "si16le", "si32be", "si32le"},
    "PIL._util": {"new"},
    "PIL.AvifImagePlugin": {"Image.register_mime", "get_codec_version"},
    "PIL.GifImagePlugin": {"Image.register_mime", "_save_netpbm", "getheader"},
    "PIL.Image": {
        "__arrow_c_array__",
        "__getstate__",
        "__repr__",
        "__setstate__",
        "_apply_env_variables",
        "_dump",
        "_reload_exif",
        "_repr_image",
        "_repr_jpeg_",
        "_repr_pretty_",
        "_repr_png_",
        "_show",
        "alpha_composite",
        "blend",
        "composite",
        "draft",
        "deprecate",
        "effect_mandelbrot",
        "effect_noise",
        "entropy",
        "eval",
        "fromarray",
        "fromarrow",
        "fromqimage",
        "fromqpixmap",
        "get_child_images",
        "getexif",
        "getextrema",
        "getmodebandnames",
        "getxmp",
        "init",
        "linear_gradient",
        "putalpha",
        "radial_gradient",
        "register_mime",
        "show",
        "thumbnail",
        "toqimage",
        "toqpixmap",
        "verify",
    },
    "PIL.ImageChops": {
        "add",
        "add_modulo",
        "blend",
        "composite",
        "constant",
        "darker",
        "difference",
        "duplicate",
        "hard_light",
        "invert",
        "lighter",
        "logical_and",
        "logical_or",
        "logical_xor",
        "multiply",
        "offset",
        "overlay",
        "screen",
        "soft_light",
        "subtract",
    },
    "PIL.ImageDraw": {
        "_color_diff",
        "_compute_regular_polygon_vertices",
        "arc",
        "bitmap",
        "chord",
        "circle",
        "ellipse",
        "floodfill",
        "getdraw",
        "regular_polygon",
        "rounded_rectangle",
        "shape",
    },
    "PIL.ImageFile": {"get_child_images", "get_format_mimetype", "verify"},
    "PIL.ImageFont": {
        "__getstate__",
        "__setstate__",
        "_load_pilfont",
        "_load_pilfont_data",
        "font_variant",
        "get_variation_axes",
        "get_variation_names",
        "getmetrics",
        "getname",
        "load_default_imagefont",
        "load_default",
        "load_path",
        "load",
        "set_variation_by_axes",
        "set_variation_by_name",
        "truetype",
    },
    "PIL.ImageMath": {"unsafe_eval"},
    "PIL.ImageOps": {
        "_color",
        "autocontrast",
        "colorize",
        "contain",
        "cover",
        "deform",
        "equalize",
        "expand",
        "exif_transpose",
        "fit",
        "grayscale",
        "mirror",
        "pad",
        "posterize",
        "solarize",
    },
    "PIL.ImagePalette": {
        "load",
        "make_gamma_lut",
        "make_linear_lut",
        "negative",
        "random",
        "sepia",
        "wedge",
    },
    "PIL.ImageSequence": {"all_frames"},
    "PIL.ImageTk": {"_get_image_from_kw", "getimage"},
    "PIL.JpegImagePlugin": {
        "Image.register_mime",
        "_getexif",
        "_getmp",
        "draft",
        "load_djpeg",
    },
    "PIL.PngImagePlugin": {"Image.register_mime", "deprecate", "getchunks", "verify"},
    "PIL.WebPImagePlugin": {"Image.register_mime"},
}


from_imports_to_skip: dict[str, set[tuple[str, str]]] = {
    "PIL.Image": {("defusedxml", "ElementTree")}
}

unused_imports_to_preserve: dict[str, set[str]] = {
    f"{IMAGE_VIEWER_NAME}.utils.os": {
        "ask_yes_no",
        "get_files_in_folder",
        "restore_file",
        "show_info",
        "trash_file",
    }
}


foldable_constants: dict[
    str,
    dict[str, FoldableConstant],
] = {
    "PIL.AvifImagePlugin": {"DECODE_CODEC_CHOICE": DECODE_CODEC_CHOICE},
    "PIL.DdsImagePlugin": {"DDS_MAGIC": DDS_MAGIC},
    "PIL.GifImagePlugin": {"_FORCE_OPTIMIZE": _FORCE_OPTIMIZE},
    "PIL.GimpGradientFile": {"EPSILON": EPSILON},
    "PIL.Image": {"WARN_POSSIBLE_FORMATS": WARN_POSSIBLE_FORMATS},
    "PIL.ImageFile": {"MAXBLOCK": MAXBLOCK},
    "PIL.ImageFont": {"MAX_STRING_LENGTH": MAX_STRING_LENGTH // 1000},
}


module_foldable_constants: dict[
    str,
    dict[str, FoldableConstant],
] = {
    IMAGE_VIEWER_NAME: {
        "__debug__": False,
        "__name__": "__main__",
        "_ERROR_COLOR": _ERROR_COLOR,
        "_MAX_ENTRY_SIZE": _MAX_ENTRY_SIZE,
        "DEFAULT_DURATION_MS": DEFAULT_DURATION_MS,
        "JPEG_MAX_DIMENSION": JPEG_MAX_DIMENSION,
        "MAX_ZOOM_RATIO_TO_SCREEN": MAX_ZOOM_RATIO_TO_SCREEN,
        "TEXT_RGB": TEXT_RGB,
        "ZOOM_AMOUNT": ZOOM_AMOUNT,
    },
    "PIL": {"SUPPORTED": True, "TYPE_CHECKING": False},
}

machine_specific_folds: dict[str, FoldableConstant] = {
    "os.name": os.name,
    "sys.byteorder": sys.byteorder,
    "sys.platform": sys.platform,
}

machine_specific_call_folds_input = TokensToFold({"os.cpu_count": os.cpu_count()})


remove_all_re = RegexReplacement("^.*$", flags=re.DOTALL)
regex_to_apply_py: dict[str, list[RegexReplacement]] = {
    f"{IMAGE_VIEWER_NAME}.utils.PIL": [RegexReplacement(r"_Image._plugins = \[\]")],
    "PIL.__init__": [
        RegexReplacement(r"_plugins = \[.*?\]", "_plugins=[]", flags=re.DOTALL),
        RegexReplacement(r"from \. import _version.*del _version", flags=re.DOTALL),
    ],
    "PIL.AvifImagePlugin": [
        RegexReplacement(
            r"try:\s+?from \. import _avif.*?SUPPORTED = False",
            "from . import _avif;SUPPORTED = True",
            flags=re.DOTALL,
        ),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r"if exif_orientation != 1 or exif:.*?self\.info\[\"exif\"\] = exif",
            flags=re.DOTALL,
        ),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r" *if exif :=.*?\n\n", flags=re.DOTALL
        ),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r'exif or b""', replacement='b""'
        ),
    ],
    "PIL.DdsImagePlugin": [
        RegexReplacement(
            r"# Backward compatibility layer.*DXGI_FORMAT_BC7_UNORM_SRGB = DXGI_FORMAT.BC7_UNORM_SRGB",  # noqa: E501
            flags=re.DOTALL,
        )
    ],
    "PIL.Image": [
        RegexReplacement(
            r"try:\n    #.*?from \. import _imaging as core.*?except.*?raise",
            "from . import _imaging as core",
            flags=re.DOTALL,
        ),
        RegexReplacement(
            "if im is None and formats is ID:.*?if im:", "if im:", flags=re.DOTALL
        ),
        RegexReplacement(r"def preinit\(\).*_initialized = 1", flags=re.DOTALL),
    ],
    "PIL.ImageDraw": [
        RegexReplacement(
            r"def Draw.*?return ImageDraw.*?\)",
            """def Draw(im,mode=None):return ImageDraw(im,mode)""",
            flags=re.DOTALL,
        ),
    ],
    "PIL.ImageFile": [
        RegexReplacement(
            r"if isinstance\(self, StubImageFile\):.*?open\(self\)",
            flags=re.DOTALL,
        ),
    ],
    "PIL.ImageFont": [
        RegexReplacement(
            r"try:.*DeferredError\.new\(ex\)",
            "from . import _imagingft as core",
            flags=re.DOTALL,
        ),
        RegexReplacement(
            r"if isinstance\(core, DeferredError\):.*?core\.ex", flags=re.DOTALL
        ),
        RegexReplacement(
            r"if layout_engine not in.*?elif.*?layout_engine = Layout\.BASIC",
            "layout_engine = Layout.BASIC",
            flags=re.DOTALL,
        ),
    ],
    "PIL.ImageMode": [
        RegexReplacement(
            "from typing import NamedTuple", "from collections import namedtuple"
        ),
        RegexReplacement(
            r"\(NamedTuple\):.*return self\.mode",
            r"(namedtuple('ModeDescriptor', ['mode','bands','basemode','basetype','typestr'])):\n\tdef __str__(self):return self.mode",  # noqa: E501
            flags=re.DOTALL,
        ),
    ],
    "PIL.ImageTk": [
        RegexReplacement("image is None:", "False:", count=0),
        RegexReplacement(r"isinstance\(image, str\):", "False:"),
    ],
    "PIL.JpegImagePlugin": [
        RegexReplacement(  # Remove .mpo support for now
            r"def jpeg_factory\(.*return im",
            "def jpeg_factory(fp,filename=None):return JpegImageFile(fp,filename)",
            flags=re.DOTALL,
        ),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r"if isinstance\(exif, Image\.Exif\):\s+exif = exif.tobytes\(\)"
        ),
    ],
    "PIL.PngImagePlugin": [
        RegexReplacement(r"raise EOFError\(.*?\)", "raise EOFError", count=0),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r"if isinstance\(exif, Image\.Exif\):\s+exif = exif.tobytes\(8\)"
        ),
    ],
    "PIL.ImageText": [
        RegexReplacement(
            r"isinstance\(self\.font, ImageFont\.TransposedFont\)",
            "self.font.__class__.__name__ == 'TransposedFont'",
        ),
    ],
    "PIL.WebPImagePlugin": [
        RegexReplacement(
            r"try:\s+?from \. import _webp.*?SUPPORTED = False",
            "from . import _webp;SUPPORTED = True",
            flags=re.DOTALL,
        ),
        RegexReplacement(  # Remove Exif usage to remove Tiff dependency
            r"if isinstance\(exif, Image\.Exif\):\s+exif = exif.tobytes\(\)", count=2
        ),
    ],
}

if os.name == "nt":
    regex_to_apply_py["PIL.AvifImagePlugin"].append(
        RegexReplacement(
            r"def _get_default_max_threads\(\).*?return os\.",
            "def _get_default_max_threads():return os.",
            flags=re.DOTALL,
        )
    )
else:
    regex_to_apply_py["send2trash.__init__"] = [remove_all_re]
    regex_to_apply_py["send2trash.compat"] = [
        RegexReplacement(
            "^.*$",
            replacement=(
                """
text_type = str
binary_type = bytes
from collections.abc import Iterable
iterable_type = Iterable
import os
environb = os.environb"""
            ),
            flags=re.DOTALL,
        )
    ]
    regex_to_apply_py["send2trash.exceptions"] = [
        RegexReplacement(
            "^.*$",
            replacement="""
import errno
class TrashPermissionError(PermissionError):
    def __init__(self, filename):
        PermissionError.__init__(self, errno.EACCES, "Permission denied", filename)""",
            flags=re.DOTALL,
        )
    ]
    # We don't use pathlib's Path, remove support for it
    regex_to_apply_py["send2trash.util"] = [
        RegexReplacement(r".*\[path\.__fspath__\(\).*\]")
    ]


# Keys are relative paths or globs. globs should target a single file
tcl_folder: str = "tcl8/*" if os.name == "nt" else "tcl/tcl8"
regex_to_apply_tk: dict[str, list[RegexReplacement]] = {
    "tk/ttk/ttk.tcl": [
        # Loads themes that are not used
        RegexReplacement(
            "proc ttk::LoadThemes.*?\n}", "proc ttk::LoadThemes {} {}", flags=re.DOTALL
        )
    ],
    f"{tcl_folder}/platform-*.tm": [
        # Discontinued OS
        RegexReplacement(r"osf1 \{.*?\}", flags=re.DOTALL),
        RegexReplacement(r"solaris(\*-\*)? \{(.*?\{.*?\}.*?)*?\}", flags=re.DOTALL),
    ],
}

if sys.platform != "darwin":
    regex_to_apply_tk[f"{tcl_folder}/platform-*.tm"].append(
        RegexReplacement(r"darwin \{.*?aix", "aix", flags=re.DOTALL)
    )

    regex_to_apply_tk["tcl/auto.tcl"] = [
        RegexReplacement(
            r'if \{\$tcl_platform\(platform\) eq "unix".*?\}.*?\}',
            flags=re.DOTALL,
        )
    ]

    regex_to_apply_tk["tcl/init.tcl"] = [
        RegexReplacement(
            r'if \{\$tcl_platform\(os\) eq "Darwin".*?else.*?\}\s*?\}',
            "package unknown {::tcl::tm::UnknownHandler ::tclPkgUnknown}",
            flags=re.DOTALL,
        )
    ]

data_files_to_exclude: list[str] = [
    "tcl/http1.0",
    "tcl/tzdata",
    "tcl*/**/http-*.tm",
    "tcl*/**/shell-*.tm",
    "tcl*/**/tcltest-*.tm",
    "tcl/parray.tcl",
    "tk/ttk/*Theme.tcl",
    "tk/images",
    "tk/msgs",
]
if sys.platform != "darwin":
    # These are Mac specific encodings
    data_files_to_exclude.append("tcl/encoding/mac*.enc")


dlls_to_include: list[str] = ["libturbojpeg.dll"]
