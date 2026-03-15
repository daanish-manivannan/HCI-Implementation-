"""
cursor_controller.py
Wraps PyAutoGUI to provide cursor movement, clicks, drag-mode, scroll,
and keyboard helpers with cooldown protection.
"""

import time
import pyautogui
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PYAUTOGUI_FAILSAFE, PYAUTOGUI_PAUSE, CLICK_COOLDOWN_SEC

pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE    = PYAUTOGUI_PAUSE


class CursorController:
    """
    Cursor and keyboard controller.

    Key methods:
        move(x, y)        – absolute cursor move
        left_click()      – single click with cooldown
        double_click()    – double click
        right_click()     – right click
        toggle_drag()     – start/stop drag (for long-blink drag mode)
        scroll(clicks)    – positive=up, negative=down
        type_text(text)   – send keystrokes
        press_key(key)    – press a named key
        hotkey(*keys)     – hotkey combination
    """

    def __init__(self):
        self._last_click_time = 0.0
        self._dragging = False

    def move(self, x, y):
        try:
            pyautogui.moveTo(int(x), int(y), duration=0)
        except pyautogui.FailSafeException:
            pass

    def _can_click(self):
        now = time.time()
        if now - self._last_click_time >= CLICK_COOLDOWN_SEC:
            self._last_click_time = now
            return True
        return False

    def left_click(self):
        if self._can_click():
            try:
                pyautogui.click()
            except pyautogui.FailSafeException:
                pass
            return True
        return False

    def double_click(self):
        if self._can_click():
            try:
                pyautogui.doubleClick()
            except pyautogui.FailSafeException:
                pass
            return True
        return False

    def right_click(self):
        if self._can_click():
            try:
                pyautogui.rightClick()
            except pyautogui.FailSafeException:
                pass
            return True
        return False

    def toggle_drag(self):
        if self._dragging:
            try:
                pyautogui.mouseUp(button="left")
            except pyautogui.FailSafeException:
                pass
            self._dragging = False
        else:
            try:
                pyautogui.mouseDown(button="left")
            except pyautogui.FailSafeException:
                pass
            self._dragging = True
        return self._dragging

    @property
    def is_dragging(self):
        return self._dragging

    def release_drag(self):
        if self._dragging:
            try:
                pyautogui.mouseUp(button="left")
            except pyautogui.FailSafeException:
                pass
            self._dragging = False

    def scroll(self, clicks):
        try:
            pyautogui.scroll(clicks)
        except pyautogui.FailSafeException:
            pass

    def type_text(self, text):
        try:
            pyautogui.typewrite(text, interval=0.05)
        except pyautogui.FailSafeException:
            pass

    def press_key(self, key):
        try:
            pyautogui.press(key)
        except pyautogui.FailSafeException:
            pass

    def hotkey(self, *keys):
        try:
            pyautogui.hotkey(*keys)
        except pyautogui.FailSafeException:
            pass
