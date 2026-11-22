import QtQuick
import QtQuick.Effects
import QtQuick.Shapes

// A Liquid Glass surface: a blurred, saturated copy of the backdrop behind it, a light
// tint, a hairline rim, a specular top edge, and a soft drop shadow.
Item {
    id: root
    property Item backdrop
    property real radius: 24
    property real tintTop: 0.13
    property real tintBottom: 0.05
    property bool shadow: true
    property Item light: null             // pointer glow source (Main's `light`)
    property int revealDelay: -1          // >= 0 plays the entrance after that many ms

    // The entrance plays once, when the panel is created; later setting changes never hide it.
    transform: Translate { id: lift }
    Component.onCompleted: if (revealDelay >= 0 && icp.animations) { opacity = 0; lift.y = 18; reveal.start() }

    SequentialAnimation {
        id: reveal
        PauseAnimation { duration: Math.max(0, root.revealDelay) }
        ParallelAnimation {
            NumberAnimation { target: root; property: "opacity"; to: 1; duration: 520; easing.type: Easing.OutCubic }
            NumberAnimation { target: lift; property: "y"; to: 0; duration: 700; easing.type: Easing.OutExpo }
        }
    }

    RectangularShadow {
        visible: root.shadow
        anchors.fill: parent
        radius: root.radius
        blur: 48
        offset.y: 22
        spread: -6
        color: Theme.glassShadow
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
            GradientStop { position: 0.0; color: Theme.dark ? Qt.rgba(1, 1, 1, root.tintTop) : Theme.glassTop }
            GradientStop { position: 1.0; color: Theme.dark ? Qt.rgba(0.85, 0.9, 1, root.tintBottom) : Theme.glassBottom }
        }
        border.width: 1
        border.color: Theme.glassRim
    }

    // Specular highlight along the top rim.
    Rectangle {
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 1 }
        height: Math.min(parent.height / 2, 46)
        radius: root.radius - 1
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, Theme.specular) }
            GradientStop { position: 1.0; color: Theme.overlay(0.0) }
        }
    }

    // Liquid sheen: a soft light that trails the pointer across the glass.
    Shape {
        id: sheen
        anchors.fill: parent
        visible: root.light !== null && icp.animations
        opacity: root.light && root.light.active ? 1 : 0
        Behavior on opacity { enabled: icp.animations; NumberAnimation { duration: 420; easing.type: Easing.OutCubic } }
        preferredRendererType: Shape.CurveRenderer
        readonly property point spot: root.light ? root.mapFromItem(root.light, root.light.px, root.light.py) : Qt.point(-1000, -1000)
        ShapePath {
            strokeColor: "transparent"
            fillGradient: RadialGradient {
                centerX: sheen.spot.x; centerY: sheen.spot.y; centerRadius: 300
                focalX: centerX; focalY: centerY
                GradientStop { position: 0.0; color: Theme.dark ? Qt.rgba(0.85, 0.92, 1, 0.11) : Qt.rgba(1, 1, 1, 0.45) }
                GradientStop { position: 0.55; color: Theme.dark ? Qt.rgba(0.85, 0.92, 1, 0.03) : Qt.rgba(1, 1, 1, 0.12) }
                GradientStop { position: 1.0; color: Qt.rgba(1, 1, 1, 0.0) }
            }
            PathRectangle { x: 0; y: 0; width: sheen.width; height: sheen.height; radius: root.radius }
        }
    }
}
