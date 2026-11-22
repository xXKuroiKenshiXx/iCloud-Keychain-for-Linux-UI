import QtQuick
import QtQuick.Shapes

// Deep night base with slow-drifting light fields; the glass panels refract this.
Item {
    id: root
    property bool reducedMotion: false

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0b1226" }
            GradientStop { position: 0.6; color: "#080c1a" }
            GradientStop { position: 1.0; color: "#05060e" }
        }
    }

    Repeater {
        model: [
            { c: "#3d82ff", x: 0.18, y: 0.10, r: 0.62, dx: 0.07, dy: 0.06, t: 23000, a: 0.62 },
            { c: "#16c6b3", x: 0.78, y: 0.82, r: 0.58, dx: -0.08, dy: -0.05, t: 29000, a: 0.50 },
            { c: "#8461ff", x: 0.86, y: 0.08, r: 0.52, dx: -0.06, dy: 0.08, t: 31000, a: 0.55 },
            { c: "#ff6aa8", x: 0.10, y: 0.92, r: 0.40, dx: 0.09, dy: -0.06, t: 37000, a: 0.40 },
            { c: "#4fd1ff", x: 0.52, y: 0.42, r: 0.36, dx: 0.10, dy: 0.08, t: 41000, a: 0.28 }
        ]
        delegate: Shape {
            id: field
            required property var modelData
            property real phase: 0
            readonly property real diameter: Math.max(root.width, root.height) * modelData.r
            width: diameter
            height: diameter
            x: root.width * (modelData.x + modelData.dx * Math.sin(phase)) - diameter / 2
            y: root.height * (modelData.y + modelData.dy * Math.cos(phase)) - diameter / 2
            preferredRendererType: Shape.CurveRenderer
            NumberAnimation on phase {
                running: !root.reducedMotion
                from: 0; to: Math.PI * 2
                duration: field.modelData.t
                loops: Animation.Infinite
            }
            ShapePath {
                strokeColor: "transparent"
                fillGradient: RadialGradient {
                    centerX: field.diameter / 2; centerY: field.diameter / 2; centerRadius: field.diameter / 2
                    focalX: centerX; focalY: centerY
                    GradientStop { position: 0.0; color: Qt.alpha(field.modelData.c, field.modelData.a) }
                    GradientStop { position: 0.45; color: Qt.alpha(field.modelData.c, field.modelData.a * 0.45) }
                    GradientStop { position: 1.0; color: Qt.alpha(field.modelData.c, 0) }
                }
                PathRectangle { x: 0; y: 0; width: field.diameter; height: field.diameter }
            }
        }
    }

    // Vignette keeps the edges deep and the text contrast high.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.0) }
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.30) }
        }
    }
}
