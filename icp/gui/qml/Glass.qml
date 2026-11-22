import QtQuick
import QtQuick.Effects

// A Liquid Glass surface: a blurred, saturated copy of the backdrop behind it, a light
// tint, a hairline rim, a specular top edge, and a soft drop shadow.
Item {
    id: root
    property Item backdrop
    property real radius: 24
    property real tintTop: 0.13
    property real tintBottom: 0.05
    property bool shadow: true

    RectangularShadow {
        visible: root.shadow
        anchors.fill: parent
        radius: root.radius
        blur: 48
        offset.y: 22
        spread: -6
        color: Qt.rgba(0, 0, 0.02, 0.55)
    }

    ShaderEffectSource {
        id: behind
        anchors.fill: parent
        visible: false
        live: true
        sourceItem: root.backdrop
        sourceRect: {
            // Re-evaluated whenever the panel moves or resizes.
            root.x; root.y; root.width; root.height
            var host = root.parent
            while (host) { host.x; host.y; host = host.parent }
            if (!root.backdrop) return Qt.rect(0, 0, 0, 0)
            var p = root.mapToItem(root.backdrop, 0, 0)
            return Qt.rect(p.x, p.y, root.width, root.height)
        }
    }

    Rectangle {
        id: shapeMask
        anchors.fill: parent
        radius: root.radius
        visible: false
        layer.enabled: true
    }

    MultiEffect {
        anchors.fill: parent
        source: behind
        blurEnabled: true
        blur: 1.0
        blurMax: 64
        saturation: 0.45
        brightness: 0.02
        maskEnabled: true
        maskSource: shapeMask
    }

    Rectangle {
        anchors.fill: parent
        radius: root.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, root.tintTop) }
            GradientStop { position: 1.0; color: Qt.rgba(0.85, 0.9, 1, root.tintBottom) }
        }
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.20)
    }

    // Specular highlight along the top rim.
    Rectangle {
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 1 }
        height: Math.min(parent.height / 2, 46)
        radius: root.radius - 1
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.16) }
            GradientStop { position: 1.0; color: Qt.rgba(1, 1, 1, 0.0) }
        }
    }
}
