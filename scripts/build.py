#!/usr/bin/env python3
"""Generates the EmberTide VS Code theme (workbench UI + syntax highlighting).

This is a companion repo to github.com/dannyc87/embertide (the terminal theme
family). The palette below is a copy of that repo's FINAL dict, not a live
reference to it -- if the terminal theme's colors change, re-sync PALETTE
here by hand. Run from the repo root: `python3 scripts/build.py`.
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Copied from github.com/dannyc87/embertide/scripts/build.py's FINAL dict.
PALETTE = {
    "background": "001219", "foreground": "e9d8a6",
    "cursor": "ee9b00", "cursor_text": "001219",
    "selection_bg": "4376c2", "selection_fg": "e9d8a6",

    "black": "001219", "red": "c23626", "green": "199647", "yellow": "ee9b00",
    "blue": "00b4d8", "magenta": "ab51e3", "cyan": "008388", "white": "e9d8a6",

    "bright_black": "6d787c", "bright_red": "da5b2d", "bright_green": "8fe259",
    "bright_yellow": "febd5c", "bright_blue": "0ad6ff", "bright_magenta": "cf76ff",
    "bright_cyan": "65dcb9", "bright_white": "f6ebca",
}


def h(role):
    return PALETTE[role]


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print("wrote", path)


def hex_to_rgb01(hexcol):
    hexcol = hexcol.lstrip('#')
    return tuple(int(hexcol[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(hexcol):
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb01(hexcol))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex1, hex2):
    l1, l2 = rel_lum(hex1), rel_lum(hex2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def verify():
    bg = PALETTE["background"]
    # sanity check: every role must at least parse as a hex color, and the
    # normal/bright accent rows should read as visibly different from bg.
    for role, hexcol in PALETTE.items():
        hex_to_rgb01(hexcol)
    for role in ["red", "green", "blue", "magenta", "cyan", "yellow"]:
        assert contrast(PALETTE[role], bg) >= 3.0, f"{role} too low-contrast to use as UI text"
    print("verify: OK —", len(PALETTE), "roles parsed, accent rows are visible against bg")


def gen_theme(variant_name, output_path, italic_keywords=False):
    hh = lambda role: f"#{h(role)}"
    fg, bg = hh('foreground'), hh('background')
    dim = hh('bright_black')          # Stone Gray -- muted UI text/borders
    accent = hh('cursor')             # Golden Orange -- the one CTA color
    sel = hh('selection_bg')          # Deep Indigo

    def alpha(hexcol, aa):
        return hexcol + aa  # hexcol already includes '#'; aa is a 2-digit hex string

    colors = {
        "foreground": fg,
        "descriptionForeground": dim,
        "errorForeground": hh('red'),
        "focusBorder": accent,
        "selection.background": alpha(sel, "aa"),

        "editor.background": bg,
        "editor.foreground": fg,
        "editorLineNumber.foreground": dim,
        "editorLineNumber.activeForeground": fg,
        "editorCursor.foreground": accent,
        "editor.selectionBackground": alpha(sel, "88"),
        "editor.inactiveSelectionBackground": alpha(sel, "44"),
        "editor.selectionHighlightBackground": alpha(sel, "33"),
        "editor.wordHighlightBackground": alpha(sel, "33"),
        "editor.findMatchBackground": alpha(hh('bright_yellow'), "66"),
        "editor.findMatchHighlightBackground": alpha(hh('bright_yellow'), "33"),
        "editor.lineHighlightBackground": alpha(dim, "22"),
        "editorIndentGuide.background1": alpha(dim, "33"),
        "editorIndentGuide.activeBackground1": alpha(dim, "77"),
        "editorWhitespace.foreground": alpha(dim, "55"),
        "editorBracketMatch.background": alpha(sel, "55"),
        "editorBracketMatch.border": accent,
        "editorGutter.background": bg,
        "editorGutter.modifiedBackground": hh('blue'),
        "editorGutter.addedBackground": hh('green'),
        "editorGutter.deletedBackground": hh('red'),
        "editorError.foreground": hh('red'),
        "editorWarning.foreground": hh('bright_yellow'),
        "editorInfo.foreground": hh('blue'),
        "editorHoverWidget.background": bg,
        "editorHoverWidget.border": alpha(dim, "77"),
        "editorSuggestWidget.background": bg,
        "editorSuggestWidget.border": alpha(dim, "77"),
        "editorSuggestWidget.selectedBackground": alpha(sel, "88"),
        "editorWidget.background": bg,
        "editorWidget.border": alpha(dim, "77"),

        "activityBar.background": bg,
        "activityBar.foreground": fg,
        "activityBar.inactiveForeground": dim,
        "activityBarBadge.background": accent,
        "activityBarBadge.foreground": hh('background'),

        "sideBar.background": bg,
        "sideBar.foreground": fg,
        "sideBarTitle.foreground": fg,
        "sideBarSectionHeader.background": bg,
        "sideBarSectionHeader.foreground": dim,

        "list.activeSelectionBackground": alpha(sel, "88"),
        "list.activeSelectionForeground": fg,
        "list.inactiveSelectionBackground": alpha(sel, "44"),
        "list.hoverBackground": alpha(dim, "22"),
        "list.highlightForeground": accent,
        "list.focusBackground": alpha(sel, "66"),

        "statusBar.background": bg,
        "statusBar.foreground": fg,
        "statusBar.noFolderBackground": bg,
        "statusBar.debuggingBackground": hh('red'),
        "statusBar.debuggingForeground": bg,
        "statusBarItem.hoverBackground": alpha(dim, "33"),
        "statusBarItem.remoteBackground": hh('cyan'),
        "statusBarItem.remoteForeground": bg,

        "titleBar.activeBackground": bg,
        "titleBar.activeForeground": fg,
        "titleBar.inactiveBackground": bg,
        "titleBar.inactiveForeground": dim,

        "editorGroupHeader.tabsBackground": bg,
        "tab.activeBackground": bg,
        "tab.activeForeground": fg,
        "tab.inactiveBackground": bg,
        "tab.inactiveForeground": dim,
        "tab.border": bg,
        "tab.activeBorder": alpha(dim, "00"),
        "tab.activeBorderTop": accent,

        "panel.background": bg,
        "panel.border": alpha(dim, "77"),
        "panelTitle.activeForeground": fg,
        "panelTitle.activeBorder": accent,
        "panelTitle.inactiveForeground": dim,

        "input.background": bg,
        "input.foreground": fg,
        "input.border": alpha(dim, "77"),
        "input.placeholderForeground": dim,
        "inputOption.activeBorder": accent,
        "dropdown.background": bg,
        "dropdown.foreground": fg,
        "dropdown.border": alpha(dim, "77"),

        "button.background": accent,
        "button.foreground": hh('background'),
        "button.hoverBackground": hh('bright_yellow'),
        "button.secondaryBackground": alpha(dim, "44"),
        "button.secondaryForeground": fg,

        "badge.background": accent,
        "badge.foreground": hh('background'),

        "scrollbarSlider.background": alpha(dim, "33"),
        "scrollbarSlider.hoverBackground": alpha(dim, "55"),
        "scrollbarSlider.activeBackground": alpha(dim, "77"),

        "notifications.background": bg,
        "notifications.foreground": fg,
        "notificationCenterHeader.background": bg,
        "notificationsErrorIcon.foreground": hh('red'),
        "notificationsWarningIcon.foreground": hh('bright_yellow'),
        "notificationsInfoIcon.foreground": hh('blue'),

        "gitDecoration.addedResourceForeground": hh('green'),
        "gitDecoration.modifiedResourceForeground": hh('bright_yellow'),
        "gitDecoration.deletedResourceForeground": hh('red'),
        "gitDecoration.untrackedResourceForeground": hh('cyan'),
        "gitDecoration.ignoredResourceForeground": dim,
        "gitDecoration.conflictingResourceForeground": hh('magenta'),

        "diffEditor.insertedTextBackground": alpha(hh('green'), "33"),
        "diffEditor.removedTextBackground": alpha(hh('red'), "33"),
        "diffEditor.insertedLineBackground": alpha(hh('green'), "22"),
        "diffEditor.removedLineBackground": alpha(hh('red'), "22"),

        "menu.background": bg,
        "menu.foreground": fg,
        "menu.selectionBackground": alpha(sel, "88"),
        "menu.selectionForeground": fg,
        "menu.separatorBackground": alpha(dim, "55"),

        "breadcrumb.foreground": dim,
        "breadcrumb.background": bg,
        "breadcrumb.focusForeground": fg,
        "breadcrumb.activeSelectionForeground": accent,

        "peekView.border": accent,
        "peekViewEditor.background": bg,
        "peekViewResult.background": bg,

        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminalCursor.background": hh('cursor_text'),
        "terminalCursor.foreground": accent,
        "terminal.selectionBackground": alpha(sel, "88"),
        "terminal.ansiBlack": hh('black'),
        "terminal.ansiRed": hh('red'),
        "terminal.ansiGreen": hh('green'),
        "terminal.ansiYellow": hh('yellow'),
        "terminal.ansiBlue": hh('blue'),
        "terminal.ansiMagenta": hh('magenta'),
        "terminal.ansiCyan": hh('cyan'),
        "terminal.ansiWhite": hh('white'),
        "terminal.ansiBrightBlack": hh('bright_black'),
        "terminal.ansiBrightRed": hh('bright_red'),
        "terminal.ansiBrightGreen": hh('bright_green'),
        "terminal.ansiBrightYellow": hh('bright_yellow'),
        "terminal.ansiBrightBlue": hh('bright_blue'),
        "terminal.ansiBrightMagenta": hh('bright_magenta'),
        "terminal.ansiBrightCyan": hh('bright_cyan'),
        "terminal.ansiBrightWhite": hh('bright_white'),
    }

    def rule(name, scopes, fg_=None, style=None):
        settings = {}
        if fg_: settings["foreground"] = fg_
        if style: settings["fontStyle"] = style
        return {"name": name, "scope": scopes, "settings": settings}

    token_colors = [
        rule("Comment", ["comment", "punctuation.definition.comment"], dim, "italic"),
        rule("String", ["string", "punctuation.definition.string"], hh('green')),
        rule("Regexp", ["string.regexp"], hh('cyan')),
        rule("Number", ["constant.numeric"], accent),
        rule("Language constant", ["constant.language", "constant.character"], hh('magenta')),
        rule("Keyword", ["keyword", "keyword.control", "storage.type", "storage.modifier"], hh('magenta'),
             "italic" if italic_keywords else None),
        rule("Control flow", ["keyword.control.flow", "keyword.control.trycatch", "keyword.control.exception"], hh('red'),
             "italic" if italic_keywords else None),
        rule("Operator", ["keyword.operator", "keyword.control.ternary",
                           "keyword.operator.ternary"], fg),
        rule("Function", ["entity.name.function", "support.function", "meta.function-call"], hh('blue')),
        rule("Class / type", ["entity.name.class", "entity.name.type", "support.class", "support.type"], hh('bright_yellow')),
        rule("Variable", ["variable"], fg),
        rule("Variable parameter", ["variable.parameter"], hh('bright_cyan')),
        rule("Language variable", ["variable.language"], hh('bright_cyan'), "italic"),
        rule("Tag", ["entity.name.tag"], hh('red')),
        rule("Attribute name", ["entity.other.attribute-name"], hh('bright_yellow')),
        rule("Decorator", ["meta.decorator", "punctuation.decorator", "entity.name.function.decorator",
                            "storage.type.annotation", "punctuation.definition.annotation", "meta.attribute"], hh('cyan')),
        rule("Punctuation", ["punctuation"], dim),
        rule("Template expression", ["punctuation.definition.template-expression", "meta.template.expression"], fg),
        rule("Markup heading", ["markup.heading"], accent, "bold"),
        rule("Markup bold", ["markup.bold"], fg, "bold"),
        rule("Markup italic", ["markup.italic"], fg, "italic"),
        rule("Markup inline code", ["markup.inline.raw"], hh('bright_cyan')),
        rule("Markup link", ["markup.underline.link"], hh('bright_blue')),
        rule("Invalid", ["invalid", "invalid.illegal"], hh('red')),
    ]

    theme = {
        "$generated": "by scripts/build.py — do not hand-edit",
        "name": variant_name,
        "type": "dark",
        "colors": colors,
        "tokenColors": token_colors,
    }
    write(output_path, json.dumps(theme, indent=2, ensure_ascii=False) + "\n")


def gen_package_json():
    package_json = {
        "name": "embertide-theme",
        "displayName": "EmberTide",
        "description": "A dark theme built and checked in OKLCH for consistent contrast, hue separation, and saturation.",
        "version": "1.0.0",
        "publisher": "dannyc87",
        "engines": {"vscode": "^1.75.0"},
        "categories": ["Themes"],
        "repository": {"type": "git", "url": "https://github.com/dannyc87/embertide-vscode"},
        "contributes": {
            "themes": [
                {"label": "EmberTide", "uiTheme": "vs-dark", "path": "./themes/embertide-color-theme.json"},
                {"label": "EmberTide Italic", "uiTheme": "vs-dark", "path": "./themes/embertide-italic-color-theme.json"}
            ]
        },
    }
    write("package.json", json.dumps(package_json, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    verify()
    gen_theme("EmberTide", "themes/embertide-color-theme.json", italic_keywords=False)
    gen_theme("EmberTide Italic", "themes/embertide-italic-color-theme.json", italic_keywords=True)
    gen_package_json()
    print("done")
