"""Collections of various bits of code that should not be included during compilation"""

import os
import re
import sys
from collections import defaultdict

from personal_python_ast_optimizer.regex.classes import RegexReplacement
from PIL.AvifImagePlugin import DECODE_CODEC_CHOICE
from PIL.DdsImagePlugin import DDS_MAGIC
from PIL.GimpGradientFile import EPSILON

from compile_utils.constants import IMAGE_VIEWER_NAME
from image_viewer.animation.frame import DEFAULT_ANIMATION_SPEED_MS
from image_viewer.config import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_FONT,
    DEFAULT_MAX_ITEMS_IN_CACHE,
)
from image_viewer.constants import TEXT_RGB
from image_viewer.image.resizer import JPEG_MAX_DIMENSION
from image_viewer.ui.rename_entry import _ERROR_COLOR

# Increment when edits to this file or module_dependencies are merged into main
SKIP_ITERATION: int = 1

# Module independent skips

decorators_to_always_skip: set[str] = {"abstractmethod", "override"}
functions_to_always_skip: set[str] = {"warn"}
no_warn_tokens = decorators_to_always_skip | functions_to_always_skip

# Module dependent skips

functions_to_skip: dict[str, set[str]] = {
    "PIL._binary": {"i8", "si16be", "si16le", "si32be", "si32le"},
    "PIL._util": {"new"},
    "PIL.AvifImagePlugin": {"get_codec_version", "register_mime"},
    "PIL.Image": {
        "__arrow_c_array__",
        "__getstate__",
        "__repr__",
        "__setstate__",
        "_apply_env_variables",
        "_dump",
        "_repr_image",
        "_repr_jpeg_",
        "_repr_pretty_",
        "_repr_png_",
        "_show",
        "alpha_composite",
        "blend",
        "composite",
        "debug",
        "deprecate",
        "effect_mandelbrot",
        "entropy",
        "fromarrow",
        "fromqimage",
        "fromqpixmap",
        "get_child_images",
        "getexif",
        "getLogger",
        "getmodebandnames",
        "getxmp",
        "linear_gradient",
        "load_from_fp",
        "putalpha",
        "radial_gradient",
        "register_mime",
        "show",
        "toqimage",
        "toqpixmap",
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
    "PIL.ImageDraw": {"_color_diff", "getdraw", "floodfill"},
    "PIL.ImageFile": {"get_format_mimetype", "verify"},
    "PIL.ImageFont": {
        "__getstate__",
        "__setstate__",
        "getmetrics",
        "load_default_imagefont",
        "load_default",
        "load_path",
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
    "PIL.ImageTk": {"_get_image_from_kw", "getimage"},
    "PIL.GifImagePlugin": {"_save_netpbm", "getheader", "register_mime"},
    "PIL.JpegImagePlugin": {"_getexif", "load_djpeg", "register_mime"},
    "PIL.PngImagePlugin": {"debug", "deprecate", "getLogger", "register_mime"},
    "PIL.WebPImagePlugin": {"register_mime"},
    "PIL.TiffTags": {"_populate"},
    f"{IMAGE_VIEWER_NAME}.actions.undoer": {"assert_never"},
}


vars_to_skip: dict[str, set[str]] = {
    "PIL.Image": {"MIME"},
    "PIL.ImageDraw": {"Outline"},
    "PIL.GifImagePlugin": {"_Palette", "format_description"},
    "PIL.JpegImagePlugin": {"format_description"},
    "PIL.PngImagePlugin": {"format_description"},
    "PIL.WebPImagePlugin": {"format_description"},
    f"{IMAGE_VIEWER_NAME}.viewer": {"_P", "_R", "_Ts"},
}

if os.name == "nt":
    vars_to_skip["PIL.AvifImagePlugin"] = {"DEFAULT_MAX_THREADS"}


classes_to_skip: dict[str, set[str]] = {
    "PIL.Image": {
        "SupportsArrayInterface",
        "SupportsArrowArrayInterface",
        "SupportsGetData",
    },
    "PIL.ImageFile": {"Parser", "PyEncoder", "StubHandler", "StubImageFile"},
    "PIL.ImageFont": {"TransposedFont"},
    "PIL.ImageOps": {"SupportsGetMesh"},
    "PIL.ImageTk": {"BitmapImage"},
    "PIL.PngImagePlugin": {"PngInfo"},
    f"{IMAGE_VIEWER_NAME}.state.base": {"StateBase"},
    f"{IMAGE_VIEWER_NAME}.state.rotation_state": {"StateBase"},
    f"{IMAGE_VIEWER_NAME}.state.zoom_state": {"StateBase"},
}


from_imports_to_skip: dict[str, set[str]] = {"PIL.Image": {"deprecate"}}

dict_keys_to_skip: dict[str, set[str]] = {}

decorators_to_skip: dict[str, set[str]] = {}

module_imports_to_skip: dict[str, set[str]] = {}

module_vars_to_fold: defaultdict[
    str,
    dict[str, str | bytes | bool | int | float | complex | None],
] = defaultdict(
    dict,
    {
        IMAGE_VIEWER_NAME: {
            "__debug__": False,
            "__name__": "__main__",
            "_ERROR_COLOR": _ERROR_COLOR,
            "DEFAULT_ANIMATION_SPEED_MS": DEFAULT_ANIMATION_SPEED_MS,
            "DEFAULT_BACKGROUND_COLOR": DEFAULT_BACKGROUND_COLOR,
            "DEFAULT_FONT": DEFAULT_FONT,
            "DEFAULT_MAX_ITEMS_IN_CACHE": DEFAULT_MAX_ITEMS_IN_CACHE,
            "JPEG_MAX_DIMENSION": JPEG_MAX_DIMENSION,
            "TEXT_RGB": TEXT_RGB,
        },
        "PIL": {
            "DECODE_CODEC_CHOICE": DECODE_CODEC_CHOICE,
            "DDS_MAGIC": DDS_MAGIC,
            "EPSILON": EPSILON,
            "SUPPORTED": True,
            "TYPE_CHECKING": False,
        },
    },
)

remove_all_re = RegexReplacement(pattern="^.*$", flags=re.DOTALL)
regex_to_apply_py: defaultdict[str, list[RegexReplacement]] = defaultdict(
    list,
    {
        f"{IMAGE_VIEWER_NAME}.util.PIL": [
            RegexReplacement(pattern=r"_Image._plugins = \[\]")
        ],
        "PIL.__init__": [
            RegexReplacement(
                pattern=r"_plugins = \[.*?\]",
                replacement="_plugins = []",
                flags=re.DOTALL,
            ),
            RegexReplacement(
                pattern=r"from \. import _version.*del _version", flags=re.DOTALL
            ),
        ],
        "PIL.AvifImagePlugin": [
            RegexReplacement(
                pattern=r"try:\s+?from \. import _avif.*?SUPPORTED = False",
                replacement="from . import _avif;SUPPORTED = True",
                flags=re.DOTALL,
                count=1,
            )
        ],
        "PIL.GifImagePlugin": [
            RegexReplacement(
                pattern="from typing import .*",
                replacement="from typing import cast;from collections import namedtuple",  # noqa: E501
                count=1,
            ),
            RegexReplacement(
                pattern=r"_Frame\(NamedTuple\)",
                replacement="_Frame(namedtuple('_Frame',['im','bbox','encoderinfo']))",
                count=1,
            ),
        ],
        "PIL.Image": [
            RegexReplacement(
                pattern="""try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None"""
            ),
            RegexReplacement(
                pattern=r"try:\n    #.*?from \. import _imaging as core.*?except.*?raise",  # noqa: E501
                replacement="from . import _imaging as core",
                flags=re.DOTALL,
            ),
            RegexReplacement(
                pattern=r"def preinit\(\).*_initialized = 1", flags=re.DOTALL
            ),
        ],
        "PIL.ImageDraw": [
            RegexReplacement(
                pattern=r"def Draw.*?return ImageDraw.*?\)",
                replacement="""def Draw(im,mode=None):return ImageDraw(im,mode)""",
                count=1,
                flags=re.DOTALL,
            ),
            RegexReplacement(pattern="(L|l)ist, "),  # codespell:ignore ist
            RegexReplacement(pattern="List", replacement="list"),
        ],
        "PIL.ImageFile": [
            RegexReplacement(
                pattern="from typing import .*",
                replacement="""from typing import IO, cast
from collections import namedtuple""",
                count=1,
            ),
            RegexReplacement(
                pattern=r"_Tile\(NamedTuple\):",
                replacement="_Tile(namedtuple('_Tile', ['codec_name', 'extents', 'offset', 'args'])):",  # noqa: E501
                count=1,
            ),
        ],
        "PIL.ImageFont": [
            RegexReplacement(
                pattern=r"try:.*DeferredError\.new\(ex\)",
                replacement="from . import _imagingft as core",
                flags=re.DOTALL,
            ),
            RegexReplacement(pattern=r"MAX_STRING_LENGTH is not None and"),
        ],
        "PIL.ImageMode": [
            RegexReplacement(
                pattern="from typing import NamedTuple",
                replacement="from collections import namedtuple",
                count=1,
            ),
            RegexReplacement(
                pattern=r"\(NamedTuple\):",
                replacement=r"(namedtuple('ModeDescriptor', ['mode', 'bands', 'basemode', 'basetype', 'typestr'])):",  # noqa: E501
                count=1,
            ),
        ],
        "PIL.ImagePalette": [RegexReplacement(pattern="tostring = tobytes")],
        "PIL.JpegImagePlugin": [
            RegexReplacement(  # Remove .mpo support for now
                r"def jpeg_factory\(.*return im",
                "def jpeg_factory(fp,filename=None):return JpegImageFile(fp,filename)",
                flags=re.DOTALL,
            )
        ],
        "PIL.PngImagePlugin": [
            RegexReplacement(
                pattern=r"raise EOFError\(.*?\)", replacement="raise EOFError"
            ),
            RegexReplacement(
                pattern="from typing import .*",
                replacement="from typing import IO, cast\nfrom collections import namedtuple",  # noqa: E501
                count=1,
            ),
            RegexReplacement(
                pattern=r"_RewindState\(NamedTuple\)",
                replacement="_RewindState(namedtuple('_RewindState', ['info', 'tile', 'seq_num']))",  # noqa: E501
            ),
            RegexReplacement(
                pattern=r"_Frame\(NamedTuple\)",
                replacement="_Frame(namedtuple('_Frame', ['im', 'bbox', 'encoderinfo']))",  # noqa: E501
            ),
        ],
        "PIL.WebPImagePlugin": [
            RegexReplacement(
                pattern=r"try:\s+?from \. import _webp.*?SUPPORTED = False",
                replacement="from . import _webp;SUPPORTED = True",
                flags=re.DOTALL,
                count=1,
            )
        ],
    },
)
if os.name == "nt":
    regex_to_apply_py["PIL.AvifImagePlugin"].append(
        RegexReplacement(
            r"def _get_default_max_threads\(\).*?or 1",
            "def _get_default_max_threads():return os.cpu_count() or 1",
            flags=re.DOTALL,
            count=1,
        )
    )
else:
    regex_to_apply_py["send2trash.__init__"] = [remove_all_re]
    regex_to_apply_py["send2trash.compat"] = [
        RegexReplacement(
            pattern="^.*$",
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
            count=1,
        )
    ]
    regex_to_apply_py["send2trash.exceptions"] = [
        RegexReplacement(
            pattern="^.*$",
            replacement="""
import errno
class TrashPermissionError(PermissionError):
    def __init__(self, filename):
        PermissionError.__init__(self, errno.EACCES, "Permission denied", filename)""",
            flags=re.DOTALL,
            count=1,
        )
    ]
    # We don't use pathlib's Path, remove support for it
    regex_to_apply_py["send2trash.util"] = [
        RegexReplacement(pattern=r".*\[path\.__fspath__\(\).*\]")
    ]


# Keys are relative paths or globs. globs should target a single file
regex_to_apply_tk: defaultdict[str, list[RegexReplacement]] = defaultdict(
    list,
    {
        "tk/ttk/ttk.tcl": [
            # Loads themes that are not used
            RegexReplacement(
                pattern="proc ttk::LoadThemes.*?\n}",
                replacement="proc ttk::LoadThemes {} {}",
                flags=re.DOTALL,
            )
        ],
        "tcl8/*/platform-*.tm": [
            # Discontinued OS
            RegexReplacement(pattern=r"osf1 \{.*?\}", count=1, flags=re.DOTALL),
            RegexReplacement(
                pattern=r"solaris(\*-\*)? \{(.*?\{.*?\}.*?)*?\}", flags=re.DOTALL
            ),
        ],
    },
)

if sys.platform != "darwin":
    regex_to_apply_tk["tcl8/*/platform-*.tm"].append(
        RegexReplacement(
            pattern=r"darwin \{.*?aix", replacement="aix", flags=re.DOTALL, count=1
        )
    )

    regex_to_apply_tk["tcl/auto.tcl"].append(
        RegexReplacement(
            pattern=r'if \{\$tcl_platform\(platform\) eq "unix".*?\}.*?\}',
            flags=re.DOTALL,
            count=1,
        )
    )

    regex_to_apply_tk["tcl/init.tcl"].append(
        RegexReplacement(
            pattern=r'if \{\$tcl_platform\(os\) eq "Darwin".*?else.*?\}\s*?\}',
            replacement="package unknown {::tcl::tm::UnknownHandler ::tclPkgUnknown}",
            flags=re.DOTALL,
            count=1,
        )
    )

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
dlls_to_exclude: list[str] = ["libcrypto-*", "vcruntime*_1.dll"]


# Custom nuitka implementation
_skippable_std_modules = [
    "__hello__",
    "__phello__",
    "_aix_support",
    "_pylong",
    "cgi",
    "cgitb",
    "difflib",
    "filecmp",
    "fileinput",
    "ftplib",
    "html",
    "json",
    "mailcap",
    "netrc",
    "nturl2path",
    "pickletools",
    "pipes",
    "pkgutil",
    "pyclbr",
    "socketserver",
    "tomllib",
    "trace",
    "webbrowser",
    "xdrlib",
]

if sys.version_info >= (3, 13):
    raise NotImplementedError(
        "cgi, cgitb, mailcap, and pipes need to be removed from _skippable_std_modules"
    )

custom_nuitka_regex: dict[str, list[RegexReplacement]] = {
    "__main__.py": [
        RegexReplacement(  # This is handled in nuitka_ext.py
            """if sys.flags.no_site == 0:
        needs_re_execution = True""",
            count=1,
        )
    ],
    "importing/Recursion.py": [
        RegexReplacement(
            r"if is_stdlib and module_name in detectStdlibAutoInclusionModules\(\)\:",
            f"""if is_stdlib and module_name in detectStdlibAutoInclusionModules():
        if module_name in {_skippable_std_modules}:
            return False, 'Excluding unnecessary parts of standard library.'""",
            count=1,
        )
    ],
}
