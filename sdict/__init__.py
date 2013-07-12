from sdict.alpha import AlphaSortedDict
from sdict.base import SortedDict
import os
import re


_dirname = os.path.dirname(os.path.realpath(__file__))
with open('%s/VERSION' % _dirname) as version_file:
    __version__ = tuple(
        [int(i) if re.match(r'^[\d]+$', i) else i
            for i in version_file.read().strip().replace('-', '.').split('.')],
    )


# Include short names for each provided class.
sdict = SortedDict
adict = AlphaSortedDict
