from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .elements import *
from .should_be import *
from .asserts_matchers_ui import *
from .region import *


__all__ = (
    'Keys', 'By', 'parent_element',
    # should_be
    'Not', 'Options', 'Attribute', 'CssClass', 'ExactTextIgnoringCase', 'TextIgnoringCase', 'TextIgnoringCase',
    'ExactText', 'ContainsText', 'MatchRegex', 'Displayed', 'Disabled', 'Enabled', 'Readonly', 'Empty', 'Hidden',
    'Present', 'Visible', 'DisplayedMenu', 'Active', 'CountElements',
    'CountWindows', 'CountFrames', 'ValidationError', 'Size', 'Coordinates', 'CssProperty', 'Condition',
    'ValidationErrorMessage', 'UrlExact', 'UrlContains', 'TitleExact',
    'TitleContains',
    # assert_that
    'is_displayed', 'is_empty', 'is_not_displayed', 'is_not_empty', 'is_not_present', 'is_present',
    # elements
    'ElementList', 'CustomList', 'Element', 'Text',
    'TextField', 'Link', 'Button', 'Region'
)