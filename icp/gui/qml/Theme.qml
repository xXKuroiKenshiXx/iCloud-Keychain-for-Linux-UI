pragma Singleton
import QtQuick

// Every colour the window uses, for the dark and the light appearance.
QtObject {
    readonly property bool dark: icp.darkMode

    readonly property color window: dark ? "#05070d" : "#e8edf5"
    readonly property color text: dark ? "#ffffff" : "#0e1628"
    readonly property color accent: dark ? "#8ec2ff" : "#1c64d8"
    readonly property color danger: dark ? "#ffb0b0" : "#b3261e"
    readonly property color warningText: dark ? "#ffe2b8" : "#7a4a00"
    readonly property color consoleText: dark ? "#d6e4ff" : "#1f2c45"
    readonly property color popup: dark ? Qt.rgba(0.07, 0.1, 0.18, 0.97) : Qt.rgba(0.99, 0.995, 1, 0.98)
    readonly property color selection: dark ? Qt.rgba(0.45, 0.65, 1, 0.30) : Qt.rgba(0.16, 0.42, 0.95, 0.15)

    // Backdrop
    readonly property var backdropStops: dark ? ["#0b1226", "#080c1a", "#05060e"] : ["#f1f5fc", "#e6ecf6", "#dde5f2"]
    readonly property real fieldStrength: dark ? 1.0 : 0.5
    readonly property real vignette: dark ? 0.30 : 0.06

    // Glass
    readonly property color glassTop: dark ? Qt.rgba(1, 1, 1, 0.13) : Qt.rgba(1, 1, 1, 0.8)
    readonly property color glassBottom: dark ? Qt.rgba(0.85, 0.9, 1, 0.05) : Qt.rgba(1, 1, 1, 0.6)
    readonly property color glassRim: dark ? Qt.rgba(1, 1, 1, 0.20) : Qt.rgba(1, 1, 1, 0.9)
    readonly property color glassShadow: dark ? Qt.rgba(0, 0, 0.02, 0.55) : Qt.rgba(0.12, 0.2, 0.4, 0.08)
    readonly property real specular: dark ? 0.16 : 0.5

    // Secondary text and lines at a given strength.
    function secondary(a) { return dark ? Qt.rgba(0.87, 0.91, 1, a) : Qt.rgba(0.1, 0.15, 0.27, Math.min(1, a + 0.2)) }
    function overlay(a) { return dark ? Qt.rgba(1, 1, 1, a) : Qt.rgba(0.08, 0.14, 0.3, a * 0.6) }
    function inset(a) { return dark ? Qt.rgba(0, 0.02, 0.08, a) : Qt.rgba(1, 1, 1, Math.min(1, a + 0.3)) }
}
