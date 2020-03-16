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
Module template.
"""

import json
from typing import Any, List, Optional, Union

import requests
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from aqt import gui_hooks
from aqt.addons import AddonManager
from aqt.main import AnkiQt
from aqt.progress import ProgressManager
from aqt.toolbar import Toolbar, TopToolbar
from aqt.utils import tooltip
from aqt.webview import AnkiWebView, WebContent


class TrackerUI:
    def __init__(self, toolbar_web: AnkiWebView, package_name: str):
        self._web = toolbar_web
        self._package_name = package_name
        self._recovered: Optional[int] = None
        self._delta: int = 0
        self._time: Optional[str] = None
        self._no_data: bool = False

    # API

    def update(self, recovered: int, time: str) -> bool:
        if recovered == self._recovered and not self._no_data:
            return False
        self._update_tracker_element(recovered, time)
        self._recovered = recovered
        self._time = time
        # tooltip(f"{recovered}, {time}")
        return True

    def set_no_data(self):
        self._no_data = True
        self._web.eval("covidNoData();")

    # GUI hooks

    def on_top_toolbar_did_init_links(self, links: List[str], toolbar: Toolbar):
        links.append(self._create_tracker_element())

    # requires >= 2.1.22
    def on_webview_will_set_content(
        self, web_content: WebContent, context: Union[Any, TopToolbar]
    ):
        if not isinstance(context, TopToolbar):
            return

        web_content.css.append(f"/_addons/{self._package_name}/web/tracker.css")
        web_content.js.append(f"/_addons/{self._package_name}/web/tracker.js")

    # Helpers

    def _get_update_js(self, recovered: int, delta: int, time: str):
        recovered_str = f"{recovered:n}"
        print(delta)
        delta_str = f"{delta:n}"
        return f"""
covidUpdate({json.dumps(recovered_str)}, {json.dumps(delta_str)}, {json.dumps(time)})
"""

    def _create_tracker_element(self):
        content = """<div id="covidTracker" tabindex="-1"></span>"""
        if self._recovered:
            content += f"""
<script>{self._get_update_js(self._recovered, self._delta, self._time)}</script>
            """
        return content

    def _update_tracker_element(self, recovered: int, time: str):
        if self._recovered is None:
            return
        delta = max(recovered - self._recovered, 0)
        self._delta = delta
        self._web.eval(self._get_update_js(recovered, delta, time))


class DataFetcher(QThread):

    # https://github.com/ExpDev07/coronavirus-tracker-api
    _API_URL = "https://coronavirus-tracker-api.herokuapp.com/recovered"

    success = pyqtSignal(object)
    error = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            r = requests.get(self._API_URL)
            r.raise_for_status()
            response = r.json()
            self.success.emit(response)
        except Exception as e:  # noqa
            self.error.emit(e)


class CovidTracker:

    extra = 500

    def __init__(self, main_window: AnkiQt):
        self._main_window = main_window
        self._data_fetcher = DataFetcher()
        self._data_fetcher.success.connect(self._on_request_succeeded)  # type: ignore
        self._data_fetcher.error.connect(self._on_request_failed)
        package_name = main_window.addonManager.addonFromModule(__name__)
        self._tracker_ui = TrackerUI(main_window.toolbarWeb, package_name)

    def run(self):
        gui_hooks.top_toolbar_did_init_links.append(
            self._tracker_ui.on_top_toolbar_did_init_links
        )
        gui_hooks.webview_will_set_content.append(
            self._tracker_ui.on_webview_will_set_content
        )
        self._on_timer_update()
        self.start_timer()
        gui_hooks.profile_will_close.append(self._on_profile_will_close)

    def start_timer(self):
        progress_manager: ProgressManager = self._main_window.progress
        self._timer = progress_manager.timer(2000, self._on_timer_update, True, False)

    def _on_profile_will_close(self):
        self._timer.stop()
        self._data_fetcher.quit()

    @pyqtSlot()
    def _on_timer_update(self):
        self._data_fetcher.start()

    # @pyqtSlot(object)
    def _on_request_succeeded(self, data: dict):
        recovered = data.get("latest")
        datetime = data.get("last_updated")

        if not recovered or not datetime:
            return False
        
        ## debugging
        recovered += self.extra
        self.extra += 500

        self._tracker_ui.update(recovered, datetime)

    def _on_request_failed(self, exception: Exception):
        self._tracker_ui.set_no_data()


def initialize_tracker(main_window: AnkiQt):
    addon_manager: AddonManager = main_window.addonManager
    addon_manager.setWebExports(__name__, r"web/.*")
    main_window._covid_tracker = CovidTracker(main_window)
    main_window._covid_tracker.run()