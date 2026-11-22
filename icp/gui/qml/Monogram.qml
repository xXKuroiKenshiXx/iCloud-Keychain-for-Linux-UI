import QtQuick

// Site tile: the website's icon on a light plate when one is cached, otherwise a rounded
// square tinted from the name with its initial.
Rectangle {
    id: root
    property string label: "?"
    property string source: ""
    property real size: 36
    readonly property bool hasIcon: source !== "" && icon.status === Image.Ready
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
        GradientStop { position: 0; color: root.hasIcon ? "#ffffff" : Qt.lighter(root.base, 1.25) }
        GradientStop { position: 1; color: root.hasIcon ? "#e9edf5" : Qt.darker(root.base, 1.25) }
    }
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, root.hasIcon ? 0.6 : 0.25)

    Image {
        id: icon
        anchors.centerIn: parent
        width: root.size * 0.68
        height: width
        source: root.source
        sourceSize.width: 128
        sourceSize.height: 128
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
        asynchronous: true
        cache: true
        visible: root.source !== ""
        opacity: status === Image.Ready ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
    }

    Text {
        anchors.centerIn: parent
        visible: !root.hasIcon
        text: (root.label.replace(/^(www\.)/, "").charAt(0) || "?").toUpperCase()
        textFormat: Text.PlainText
        color: "white"
        font.pixelSize: Math.round(root.size * 0.44)
        font.weight: Font.Bold
    }
}
