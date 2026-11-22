import QtQuick

// Site tile: a rounded square tinted from the name, with its initial.
Rectangle {
    id: root
    property string label: "?"
    property real size: 36
    width: size
    height: size
    radius: size * 0.27

    readonly property var tones: ["#4f8cff", "#2bb5a3", "#8a6cff", "#ff7a59", "#f0b429", "#e5568f", "#3fa7d6", "#6fbf4a"]
    readonly property color base: {
        var h = 0
        for (var i = 0; i < label.length; i++) h = (h * 31 + label.charCodeAt(i)) % 9973
        return tones[h % tones.length]
    }

    gradient: Gradient {
        GradientStop { position: 0; color: Qt.lighter(root.base, 1.25) }
        GradientStop { position: 1; color: Qt.darker(root.base, 1.25) }
    }
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, 0.25)

    Text {
        anchors.centerIn: parent
        text: (root.label.replace(/^(www\.)/, "").charAt(0) || "?").toUpperCase()
        color: "white"
        font.pixelSize: Math.round(root.size * 0.44)
        font.weight: Font.Bold
    }
}
