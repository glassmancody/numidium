from __future__ import annotations

from typing import cast

from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QToolButton,
    QWidget,
)

from numidium.ui.editordock import EditorDock
from numidium.ui.extensions_dock import ExtensionsDock
from numidium.ui.modsdock import ModsDock
from numidium.ui.settingsdock import SettingsDock


class ActivityBarItem(QListWidgetItem):
    """A custom widget that can be added to the application activity bar."""

    hovered = cast(SignalInstance, Signal())
    toggled = cast(SignalInstance, Signal(bool))
    triggered = cast(SignalInstance, Signal())

    _action: QAction
    _button: QToolButton
    _widget: QWidget

    def __init__(self, widget: QWidget, icon: QIcon | str, text: str):
        super().__init__()

        self.setIcon(QIcon(icon) if isinstance(icon, str) else icon)
        self.setText(text)

        font = self.font()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)

        # The associated window that is visible while active.
        self._widget = widget

        # Make an action that forwards its events to the widget.
        self._action = QAction(self.icon(), text)
        self._action.setCheckable(True)
        self._action.hovered.connect(self.hovered.emit)
        self._action.toggled.connect(self.toggled.emit)
        self._action.triggered.connect(self.triggered.emit)

        # Add the tool button to the activity bar. This lets us show the text within the bar.
        self._button = QToolButton()
        self._button.setDefaultAction(self._action)
        self._button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


class ActivityBar(QDockWidget):
    """The application window's activity bar.

    This is the left-most area of the application window. It contains a list of
    `ActivityBarItem` objects that when selected will display their associated
    widget in the main window's viewport.
    """

    # Container for ActivityBarItem widgets.
    _list: QListWidget

    # Container for associated view widgets.
    _view: QStackedWidget

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._view = QStackedWidget(parent=self)

        self._list = QListWidget(parent=self)
        self._list.setIconSize(QSize(28, 28))
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.currentItemChanged.connect(self.set_current_item)

        # Customize Look

        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.setTitleBarWidget(QWidget())  # hide title bar
        self.setMinimumWidth(self._list.iconSize().width() + 12)
        self.setWidget(self._list)

        # Default Items

        self.add_item(
            ActivityBarItem(
                widget=ModsDock(),
                icon="icons:widgets_24dp.svg",
                text="Mods",
            )
        )
        self.add_item(
            ActivityBarItem(
                widget=EditorDock(),
                icon="icons:flip_to_front_24dp.svg",
                text="Editor",
            )
        )
        self.add_item(
            ActivityBarItem(
                widget=ExtensionsDock(),
                icon="icons:settings_24dp.svg",
                text="Extensions",
            )
        )
        self.add_item(
            ActivityBarItem(
                widget=SettingsDock(),
                icon="icons:settings_24dp.svg",
                text="Settings",
            )
        )

    def add_item(self, item: ActivityBarItem) -> None:
        self._list.addItem(item)
        self._view.addWidget(item._widget)

    def remove_item(self, item: ActivityBarItem) -> None:
        i = self._list.indexFromItem(item).row()
        if i != -1:
            self._list.takeItem(i)
            self._view.removeWidget(item._widget)

    def set_current_item(self, item: ActivityBarItem) -> None:
        i = self._list.indexFromItem(item).row()
        if i != -1:
            self._list.setCurrentRow(i)
            self._view.setCurrentIndex(i)