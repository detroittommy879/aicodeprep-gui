import os
import random
import logging
import re
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork

logger = logging.getLogger(__name__)

ADS_URL = "https://wuu73.org/aicp/ads/ads.md"
AD_CACHE_FILENAME = "ads_cache.md"
AD_METADATA_FILENAME = "ads_metadata.json"


class AdManager(QtCore.QObject):
    # Emits a dictionary with title, content, link
    ad_changed = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ads = []
        self.current_ad_index = -1
        self.network_manager = QtNetwork.QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_fetch_finished)

        # Determine cache location (~/.aicodeprep-gui/)
        from aicodeprep_gui.config import get_config_dir
        self.config_dir = get_config_dir()
        self.cache_path = self.config_dir / AD_CACHE_FILENAME
        self.metadata_path = self.config_dir / AD_METADATA_FILENAME

        self.rotation_timer = QtCore.QTimer(self)
        self.rotation_timer.timeout.connect(self.rotate_ad)

        # Load existing ads from cache first
        self._load_from_cache()

        # Initial ad
        if self.ads:
            self.current_ad_index = random.randint(0, len(self.ads) - 1)
            QtCore.QTimer.singleShot(0, lambda: self.ad_changed.emit(
                self.ads[self.current_ad_index]))
            self.rotation_timer.start(60000)  # 1 minute rotation

        # Fetch new ads if needed
        self._maybe_fetch_ads()

    def _maybe_fetch_ads(self):
        """Fetch ads on every app start for now, but gracefully."""
        logger.info("Fetching fresh ads...")
        self.network_manager.get(
            QtNetwork.QNetworkRequest(QtCore.QUrl(ADS_URL)))

    def _on_fetch_finished(self, reply):
        if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
            try:
                # Use errors='replace' to handle non-UTF-8 characters (like 0x97 em-dash)
                content = reply.readAll().data().decode('utf-8', errors='replace')
                self._save_to_cache(content)
                self._parse_ads(content)

                # Update metadata
                import json
                try:
                    with open(self.metadata_path, 'w') as f:
                        json.dump(
                            {'last_fetch': datetime.now().timestamp()}, f)
                except Exception:
                    pass

                # If we didn't have ads before, start now
                if self.ads and self.current_ad_index == -1:
                    self.rotate_ad()
                    self.rotation_timer.start(60000)
            except Exception as e:
                logger.error(f"Error processing fetched ads: {e}")
        else:
            logger.debug(f"Failed to fetch ads: {reply.errorString()}")
        reply.deleteLater()

    def _save_to_cache(self, content):
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to cache ads: {e}")

    def _load_from_cache(self):
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                self._parse_ads(content)
            except Exception as e:
                logger.error(f"Failed to load ads from cache: {e}")

    def _parse_ads(self, text):
        new_ads = []
        # Support both ---AD--- ... ---END--- and ---AD--- ... ---AD--- or end of file
        ad_blocks = re.split(r'---AD---', text)
        for block in ad_blocks:
            block = block.split('---END---')[0].strip()
            if not block:
                continue

            lines = block.splitlines()
            title = ""
            content_lines = []
            link = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('## '):
                    title = line[3:].strip()
                elif line.startswith('[') and '](' in line:
                    # Very simple markdown link parser
                    match = re.search(r'\[(.*?)\]\((.*?)\)', line)
                    if match:
                        link_text = match.group(1)
                        link_url = match.group(2)
                        link = (link_text, link_url)
                else:
                    content_lines.append(line)

            if title or content_lines:
                new_ads.append({
                    'title': title,
                    'content': "\n".join(content_lines),
                    'link': link
                })

        if new_ads:
            self.ads = new_ads

    def rotate_ad(self):
        if not self.ads:
            return

        if len(self.ads) > 1:
            prev_index = self.current_ad_index
            while self.current_ad_index == prev_index:
                self.current_ad_index = random.randint(0, len(self.ads) - 1)
        else:
            self.current_ad_index = 0

        self.ad_changed.emit(self.ads[self.current_ad_index])


class AdWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.title_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.title_label.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        font = self.title_label.font()
        font.setBold(True)
        font.setPointSize(11)
        self.title_label.setFont(font)

        self.content_label = QtWidgets.QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.content_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.content_label.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        self.link_button = QtWidgets.QPushButton()
        self.link_button.setFlat(True)
        self.link_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.link_button.setStyleSheet(
            "color: #00c3ff; text-decoration: underline; font-weight: bold; text-align: right;")
        self.link_button.setVisible(False)
        self.link_url = ""
        self.link_button.clicked.connect(self._on_link_clicked)
        self.link_button.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)
        layout.addWidget(self.link_button, 0, QtCore.Qt.AlignRight)
        layout.addStretch(1)

        self.flash_timer = QtCore.QTimer(self)
        self.flash_timer.timeout.connect(self._do_flash)
        self.flash_count = 0

        self.repeat_timer = QtCore.QTimer(self)
        self.repeat_timer.setInterval(4000)  # 4 seconds between flash bursts
        self.repeat_timer.timeout.connect(self._start_flash)

        self.is_dark = False
        self.base_font_size = None
        self.setMinimumHeight(60)
        self.setVisible(False)

    def set_ad(self, ad_data):
        self.title_label.setText(ad_data.get('title', ''))
        self.content_label.setText(ad_data.get('content', ''))

        link = ad_data.get('link')
        if link:
            self.link_button.setText(link[0])
            self.link_url = link[1]
            self.link_button.setVisible(True)
        else:
            self.link_button.setVisible(False)

        self.setVisible(True)
        self._start_flash()
        self.repeat_timer.start()

    def update_theme(self, is_dark_mode):
        self.is_dark = is_dark_mode
        if is_dark_mode:
            self.content_label.setStyleSheet(
                "color: rgba(204, 204, 204, 180);")
            self.title_label.setStyleSheet("color: rgba(255, 255, 255, 200);")
            self.setStyleSheet(
                "AdWidget { background-color: rgba(20, 20, 20, 90); border: 1px solid rgba(255, 255, 255, 30); border-radius: 6px; }")
        else:
            self.content_label.setStyleSheet("color: rgba(68, 68, 68, 150);")
            self.title_label.setStyleSheet("color: rgba(0, 0, 0, 180);")
            self.setStyleSheet(
                "AdWidget { background-color: rgba(255, 255, 255, 120); border: 1px solid rgba(0, 0, 0, 25); border-radius: 6px; }")

    def wheelEvent(self, event):
        parent = self.parent()
        if parent and hasattr(parent, "viewport"):
            QtWidgets.QApplication.sendEvent(parent.viewport(), event)
            return
        super().wheelEvent(event)

    def update_base_font_size(self, base_point_size):
        if not base_point_size:
            return
        self.base_font_size = base_point_size
        point_size = max(7, int(base_point_size) - 1)
        title_font = QtGui.QFont(self.title_label.font())
        title_font.setPointSize(point_size)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        content_font = QtGui.QFont(self.content_label.font())
        content_font.setPointSize(point_size)
        self.content_label.setFont(content_font)

    def _on_link_clicked(self):
        if self.link_url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.link_url))

    def _start_flash(self):
        self.flash_count = 0
        self.flash_timer.start(250)

    def _do_flash(self):
        self.flash_count += 1
        if self.flash_count >= 5:  # Flash 2-3 times
            self.flash_timer.stop()
            self._set_label_color(None)  # Reset to default
            return

        # Flash between bright color and normal
        if self.flash_count % 2 == 1:
            # Bright orange/gold for contrast
            self._set_label_color("#ffaa00")
        else:
            self._set_label_color(None)

    def _set_label_color(self, color):
        if color:
            self.title_label.setStyleSheet(
                f"color: {color}; font-weight: bold;")
        else:
            # Revert to theme-based translucent color
            if self.is_dark:
                self.title_label.setStyleSheet(
                    "color: rgba(255, 255, 255, 200);")
            else:
                self.title_label.setStyleSheet("color: rgba(0, 0, 0, 180);")
