# -*- coding: utf-8 -*-

# Coronavirus Tracker Add-on for Anki
#
# Copyright (C) 2020  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Options dialog and associated components
"""

from aqt import mw
from aqt.qt import *

from ..libaddon.gui.dialog_options import OptionsDialog
from ..libaddon.platform import PLATFORM
from ..config import config

from .forms import options as qtform_options


__all__ = ["AddonOptions", "invokeOptionsDialog"]


class AddonOptions(OptionsDialog):

    """
    Add-on-specific options dialog implementation
    """

    # Example config:
    # _mapped_widgets = (
    #     ("form.selList", (
    #         # order is important (e.g. to set-up items before current item)
    #         ("items", {
    #             "dataPath": "synced/listitems",
    #             "setter": "_setListItems",
    #             "getter": "_getListItems"
    #         }),
    #         ("value", {
    #             "dataPath": "synced/listvalue",
    #             "setter": "_setListValue",
    #             "getter": "_getListValue"
    #         }),
    #     )),
    #     ("form.cbMain", (
    #         ("value", {
    #             "dataPath": "profile/subpath/main"
    #         }),
    #     )),
    #     ("form.dateLimData", (
    #         ("value", {
    #             "dataPath": "synced/limdate",
    #             "getter": "_getDateLimData"
    #         }),
    #         ("min", {
    #             "setter": "_setDateLimDataMin"
    #         }),
    #         ("max", {
    #             "setter": "_setDateLimDataMax"
    #         }),
    #     ))
    # )

    _mapped_widgets = tuple()

    def __init__(self, config, mw, parent=None, **kwargs):
        # Mediator methods defined in mapped_widgets might need access to
        # certain instance attributes. As super().__init__ calls these
        # mediator methods it is important that we set the attributes
        # beforehand:
        self.parent = parent or mw
        self.mw = mw
        super(AddonOptions, self).__init__(self._mapped_widgets, config,
                                           form_module=qtform_options,
                                           parent=self.parent, **kwargs)
        # Instance methods that modify the initialized UI should either be
        # called from self._setupUI or from here

    # UI adjustments

    def _setupUI(self):
        super(AddonOptions, self)._setupUI()

        # manually adjust title label font sizes on Windows
        # gap between default windows font sizes and sizes that work well
        # on Linux and macOS is simply too big
        # TODO: find a better solution
        if PLATFORM == "win":
            default_size = QApplication.font().pointSize()
            for label in [self.form.fmtLabContrib, self.form.labHeading]:
                font = label.font()
                font.setPointSize(int(default_size * 1.5))
                label.setFont(font)

    # Events:

    def _setupEvents(self):
        super(AddonOptions, self)._setupEvents()
        pass

    # Actions:

    # Helpers:

    # Config setters:

    # Config getters:


def invokeOptionsDialog(parent=None):
    """Call settings dialog"""
    dialog = AddonOptions(config, mw, parent=parent)
    return dialog.exec_()


def initializeOptions():
    config.setConfigAction(invokeOptionsDialog)
    # Set up menu entry:
    options_action = QAction("Coronavirus Tracker Options...", mw)
    options_action.triggered.connect(lambda _: invokeOptionsDialog())
    mw.form.menuTools.addAction(options_action)
