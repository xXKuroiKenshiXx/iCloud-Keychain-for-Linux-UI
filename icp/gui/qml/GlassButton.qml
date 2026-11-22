import QtQuick

// Capsule button. `prominent` is the filled accent action; otherwise a clear glass pill.
Item {
    id: root
    property string text: ""
    property string icon: ""
    property bool prominent: false
    property bool destructive: false
    property bool compact: false
    signal clicked()

    implicitHeight: compact ? 30 : 38
    implicitWidth: row.implicitWidth + (compact ? 24 : 34)
    opacity: enabled ? 1 : 0.45
    activeFocusOnTab: enabled
    Keys.onReturnPressed: if (enabled) clicked()
    Keys.onSpacePressed: if (enabled) clicked()

    Rectangle {
        id: body
        anchors.fill: parent
        radius: height / 2
        scale: mouse.pressed ? 0.97 : 1
        Behavior on scale { enabled: icp.animations; NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
        gradient: Gradient {
            GradientStop {
                position: 0
                color: root.prominent ? (root.destructive ? "#ff6b6b" : "#5aa3ff")
                                      : Theme.overlay(mouse.containsMouse ? 0.20 : 0.12)
            }
            GradientStop {
                position: 1
                color: root.prominent ? (root.destructive ? "#e0414b" : "#2f7bf6")
                                      : Theme.overlay(mouse.containsMouse ? 0.12 : 0.06)
            }
        }
        border.width: 1
        border.color: root.activeFocus ? "#9cc8ff" : root.prominent ? Qt.rgba(1, 1, 1, 0.35) : Theme.overlay(0.18)
    }

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 7
        Icon {
            visible: root.icon !== ""
            name: root.icon
            size: root.compact ? 14 : 16
            color: root.prominent ? "white" : Theme.text
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: root.text
            visible: root.text !== ""
            color: root.prominent ? "white" : Theme.text
            font.pixelSize: root.compact ? 13 : 14
            font.weight: Font.DemiBold
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
