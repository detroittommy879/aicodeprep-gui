# Custom Multi-State Widget Implementations for PySide6

This document provides comprehensive examples for creating custom widgets with more than 3 states, inspired by patterns found in the PySide6 examples repository.

## Table of Contents

1. [Custom Painted Multi-State Widget](#custom-painted-multi-state-widget)
2. [Star Rating Widget (5-State)](#star-rating-widget-5-state)
3. [Progress State Widget](#progress-state-widget)
4. [Traffic Light Style Multi-State](#traffic-light-style-multi-state)
5. [Slider-Style Multi-State Widget](#slider-style-multi-state-widget)

## Custom Painted Multi-State Widget

Based on the painting examples in the repository, here's a comprehensive multi-state widget with custom painting:

```python
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from enum import IntEnum
import sys

class MultiState(IntEnum):
    DISABLED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    MAXIMUM = 5

class CustomMultiStateWidget(QWidget):
    """A custom widget supporting 6 different states with visual feedback."""
    
    stateChanged = Signal(int)
    
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._state = MultiState.DISABLED
        self._text = text
        self._hover = False
        
        # Visual properties
        self._colors = {
            MultiState.DISABLED: QColor(128, 128, 128),
            MultiState.LOW: QColor(0, 255, 0),
            MultiState.MEDIUM: QColor(128, 255, 0),
            MultiState.HIGH: QColor(255, 255, 0),
            MultiState.CRITICAL: QColor(255, 128, 0),
            MultiState.MAXIMUM: QColor(255, 0, 0)
        }
        
        self._state_names = {
            MultiState.DISABLED: "Disabled",
            MultiState.LOW: "Low",
            MultiState.MEDIUM: "Medium", 
            MultiState.HIGH: "High",
            MultiState.CRITICAL: "Critical",
            MultiState.MAXIMUM: "Maximum"
        }
        
        self.setMinimumSize(150, 40)
        self.setMouseTracking(True)
        
    def state(self):
        return self._state
        
    def setState(self, state):
        if self._state != state and MultiState.DISABLED <= state <= MultiState.MAXIMUM:
            self._state = state
            self.stateChanged.emit(state)
            self.update()
            
    def stateName(self):
        return self._state_names.get(self._state, "Unknown")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Cycle forward through states
            next_state = (self._state + 1) % (MultiState.MAXIMUM + 1)
            self.setState(next_state)
        elif event.button() == Qt.MouseButton.RightButton:
            # Cycle backward through states
            prev_state = (self._state - 1) % (MultiState.MAXIMUM + 1)
            self.setState(prev_state)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
        
    def sizeHint(self):
        return QSize(150, 40)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Draw border
        border_color = QColor(0, 0, 0) if not self._hover else QColor(0, 0, 255)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRoundedRect(rect, 5, 5)
        
        # Draw state indicator
        indicator_rect = QRect(rect.x() + 5, rect.y() + 5, 30, rect.height() - 10)
        
        if self._state == MultiState.DISABLED:
            # Draw empty indicator for disabled state
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(QColor(128, 128, 128), 1))
        else:
            # Draw filled indicator with state color
            color = self._colors[self._state]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(150), 1))
            
        painter.drawRoundedRect(indicator_rect, 3, 3)
        
        # Draw state level bars
        if self._state > MultiState.DISABLED:
            bar_width = indicator_rect.width() // 5
            bar_height = indicator_rect.height() // 5
            
            for i in range(self._state):
                bar_rect = QRect(
                    indicator_rect.x() + 2,
                    indicator_rect.bottom() - 2 - (i + 1) * (bar_height + 1),
                    bar_width,
                    bar_height
                )
                painter.fillRect(bar_rect, QColor(255, 255, 255, 180))
        
        # Draw text
        text_rect = QRect(indicator_rect.right() + 10, rect.y(), 
                         rect.width() - indicator_rect.width() - 15, rect.height())
        
        painter.setPen(QPen(QColor(0, 0, 0)))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        
        # Main text
        if self._text:
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self._text)
        
        # State name (smaller, below main text)
        font.setPointSize(8)
        painter.setFont(font)
        state_text_rect = QRect(text_rect.x(), text_rect.y() + text_rect.height() // 2,
                               text_rect.width(), text_rect.height() // 2)
        painter.setPen(QPen(self._colors[self._state]))
        painter.drawText(state_text_rect, Qt.AlignmentFlag.AlignTop, self.stateName())

class MultiStateExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Custom Multi-State Widgets")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Left click: next state, Right click: previous state")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Create multiple widgets
        self.widgets = []
        for i in range(4):
            widget = CustomMultiStateWidget(f"System {i+1}")
            widget.stateChanged.connect(lambda state, idx=i: self.on_state_changed(idx, state))
            self.widgets.append(widget)
            layout.addWidget(widget)
            
        # Control buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset All")
        reset_button.clicked.connect(self.reset_all)
        
        random_button = QPushButton("Randomize")
        random_button.clicked.connect(self.randomize_all)
        
        button_layout.addWidget(reset_button)
        button_layout.addWidget(random_button)
        layout.addLayout(button_layout)
        
        # Status display
        self.status_label = QLabel("Click widgets to change states")
        layout.addWidget(self.status_label)
        
    def on_state_changed(self, widget_index, state):
        widget = self.widgets[widget_index]
        self.status_label.setText(f"System {widget_index+1}: {widget.stateName()}")
        
    def reset_all(self):
        for widget in self.widgets:
            widget.setState(MultiState.DISABLED)
            
    def randomize_all(self):
        import random
        for widget in self.widgets:
            state = random.randint(MultiState.DISABLED, MultiState.MAXIMUM)
            widget.setState(state)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiStateExample()
    window.show()
    sys.exit(app.exec())
```

## Star Rating Widget (5-State)

Inspired by the star delegate example in the repository:

```python
from PySide6.QtCore import Qt, Signal, QRect, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
import sys
import math

class StarRatingWidget(QWidget):
    """A 5-star rating widget with half-star precision (10 states total)."""
    
    ratingChanged = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rating = 0.0  # 0.0 to 5.0 in 0.5 increments
        self._star_size = 20
        self._star_count = 5
        
        self.setMinimumSize(self._star_size * self._star_count + 10, self._star_size + 10)
        
    def rating(self):
        return self._rating
        
    def setRating(self, rating):
        rating = max(0.0, min(5.0, rating))
        if self._rating != rating:
            self._rating = rating
            self.ratingChanged.emit(rating)
            self.update()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate which star was clicked
            x = event.position().x() - 5
            star_index = int(x // self._star_size)
            
            if 0 <= star_index < self._star_count:
                # Determine if it's left or right half of the star
                star_x = x % self._star_size
                if star_x < self._star_size / 2:
                    new_rating = star_index + 0.5
                else:
                    new_rating = star_index + 1.0
                    
                self.setRating(new_rating)
        super().mousePressEvent(event)
        
    def _create_star_polygon(self, center, size):
        """Create a star polygon centered at the given point."""
        star = QPolygonF()
        
        # Star with 5 points
        for i in range(10):
            angle = i * math.pi / 5.0
            if i % 2 == 0:
                # Outer points
                radius = size / 2.0
            else:
                # Inner points
                radius = size / 4.0
                
            x = center.x() + radius * math.cos(angle - math.pi / 2.0)
            y = center.y() + radius * math.sin(angle - math.pi / 2.0)
            star.append(QPointF(x, y))
            
        return star
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i in range(self._star_count):
            center = QPointF(5 + i * self._star_size + self._star_size / 2, 
                           self.height() / 2)
            star_polygon = self._create_star_polygon(center, self._star_size * 0.8)
            
            # Determine fill level for this star
            star_rating = self._rating - i
            
            if star_rating <= 0:
                # Empty star
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            elif star_rating >= 1.0:
                # Full star
                painter.setPen(QPen(QColor(255, 215, 0), 1))
                painter.setBrush(QBrush(QColor(255, 215, 0)))
            else:
                # Half star - this is simplified; a real implementation would clip
                painter.setPen(QPen(QColor(255, 215, 0), 1))
                painter.setBrush(QBrush(QColor(255, 215, 0, 128)))
                
            painter.drawPolygon(star_polygon)

class StarRatingExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Click stars to set rating:"))
        
        self.star_widget = StarRatingWidget()
        self.star_widget.ratingChanged.connect(self.on_rating_changed)
        layout.addWidget(self.star_widget)
        
        self.rating_label = QLabel("Rating: 0.0 / 5.0")
        layout.addWidget(self.rating_label)
        
    def on_rating_changed(self, rating):
        self.rating_label.setText(f"Rating: {rating:.1f} / 5.0")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StarRatingExample()
    window.show()
    sys.exit(app.exec())
```

## Progress State Widget

A widget that shows discrete progress states with visual feedback:

```python
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from enum import IntEnum
import sys

class ProgressState(IntEnum):
    NOT_STARTED = 0
    INITIALIZING = 1
    IN_PROGRESS = 2
    NEARLY_COMPLETE = 3
    COMPLETE = 4
    ERROR = 5

class ProgressStateWidget(QWidget):
    """A widget showing discrete progress states with visual indicators."""
    
    stateChanged = Signal(int)
    
    def __init__(self, label="", parent=None):
        super().__init__(parent)
        self._state = ProgressState.NOT_STARTED
        self._label = label
        
        self._state_info = {
            ProgressState.NOT_STARTED: ("Not Started", QColor(200, 200, 200)),
            ProgressState.INITIALIZING: ("Initializing", QColor(100, 150, 255)),
            ProgressState.IN_PROGRESS: ("In Progress", QColor(255, 200, 0)),
            ProgressState.NEARLY_COMPLETE: ("Nearly Complete", QColor(150, 255, 100)),
            ProgressState.COMPLETE: ("Complete", QColor(0, 255, 0)),
            ProgressState.ERROR: ("Error", QColor(255, 0, 0))
        }
        
        self.setMinimumSize(200, 50)
        
    def state(self):
        return self._state
        
    def setState(self, state):
        if self._state != state and state in self._state_info:
            self._state = state
            self.stateChanged.emit(state)
            self.update()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Cycle through normal states (skip ERROR unless already in ERROR)
            if self._state == ProgressState.ERROR:
                next_state = ProgressState.NOT_STARTED
            elif self._state == ProgressState.COMPLETE:
                next_state = ProgressState.NOT_STARTED
            else:
                next_state = self._state + 1
            self.setState(next_state)
        elif event.button() == Qt.MouseButton.RightButton:
            # Set to error state
            self.setState(ProgressState.ERROR)
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Get state info
        state_name, state_color = self._state_info[self._state]
        
        # Draw background
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(250, 250, 250)))
        painter.drawRoundedRect(rect, 5, 5)
        
        # Draw progress bar
        progress_rect = QRect(rect.x() + 10, rect.bottom() - 15, rect.width() - 20, 8)
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawRoundedRect(progress_rect, 4, 4)
        
        # Fill progress based on state
        if self._state != ProgressState.NOT_STARTED:
            if self._state == ProgressState.ERROR:
                fill_width = progress_rect.width()
                fill_color = state_color
            else:
                progress_values = {
                    ProgressState.INITIALIZING: 0.2,
                    ProgressState.IN_PROGRESS: 0.5,
                    ProgressState.NEARLY_COMPLETE: 0.8,
                    ProgressState.COMPLETE: 1.0
                }
                fill_width = int(progress_rect.width() * progress_values.get(self._state, 0))
                fill_color = state_color
                
            if fill_width > 0:
                fill_rect = QRect(progress_rect.x(), progress_rect.y(), fill_width, progress_rect.height())
                
                # Create gradient for smooth appearance
                gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
                gradient.setColorAt(0, fill_color.lighter(120))
                gradient.setColorAt(1, fill_color)
                
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(fill_rect, 4, 4)
        
        # Draw label and state text
        text_rect = QRect(rect.x() + 10, rect.y() + 5, rect.width() - 20, progress_rect.y() - rect.y() - 10)
        
        painter.setPen(QPen(QColor(0, 0, 0)))
        if self._label:
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, self._label)
            
        painter.setPen(QPen(state_color))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, state_name)

class ProgressStateExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Progress State Widgets (Left click: advance, Right click: error)"))
        
        # Create multiple progress widgets
        self.progress_widgets = []
        tasks = ["Download Files", "Process Data", "Generate Report", "Send Email"]
        
        for task in tasks:
            widget = ProgressStateWidget(task)
            widget.stateChanged.connect(lambda state, t=task: self.on_state_changed(t, state))
            self.progress_widgets.append(widget)
            layout.addWidget(widget)
            
        # Control buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self.reset_all)
        
        complete_btn = QPushButton("Complete All")
        complete_btn.clicked.connect(self.complete_all)
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(complete_btn)
        layout.addLayout(button_layout)
        
        self.status_label = QLabel("Click widgets to change states")
        layout.addWidget(self.status_label)
        
    def on_state_changed(self, task, state):
        state_names = {
            ProgressState.NOT_STARTED: "Not Started",
            ProgressState.INITIALIZING: "Initializing",
            ProgressState.IN_PROGRESS: "In Progress", 
            ProgressState.NEARLY_COMPLETE: "Nearly Complete",
            ProgressState.COMPLETE: "Complete",
            ProgressState.ERROR: "Error"
        }
        self.status_label.setText(f"{task}: {state_names[state]}")
        
    def reset_all(self):
        for widget in self.progress_widgets:
            widget.setState(ProgressState.NOT_STARTED)
            
    def complete_all(self):
        for widget in self.progress_widgets:
            widget.setState(ProgressState.COMPLETE)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProgressStateExample()
    window.show()
    sys.exit(app.exec())
```

These custom multi-state widgets demonstrate:

1. **Custom Painting**: Using QPainter for sophisticated visual representations
2. **State Management**: Proper enum-based state handling with validation
3. **User Interaction**: Mouse event handling for state changes
4. **Visual Feedback**: Different colors, gradients, and shapes for each state
5. **Extensibility**: Easy to modify for different numbers of states or visual styles

Each widget can be easily customized for specific use cases by modifying the state definitions, colors, and painting logic.