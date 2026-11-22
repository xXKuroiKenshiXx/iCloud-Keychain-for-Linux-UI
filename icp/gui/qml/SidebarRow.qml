import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Rectangle {
    id: root
    property string label
    property string icon
    property string badge: ""
    property string detail: ""
    property bool active: false
    property bool compact: false
    signal clicked()

    implicitHeight: 38
    radius: 10
    color: active ? Theme.overlay(0.16) : (mouse.containsMouse ? Theme.overlay(0.07) : "transparent")
    Behavior on color { enabled: icp.animations; ColorAnimation { duration: 120 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 10
        Icon { name: root.icon; size: 17; color: root.active ? Theme.accent : Theme.secondary(0.8) }
        Text {
            visible: !root.compact
            text: root.label
            color: Theme.text
            font.pixelSize: 13 + 1
            font.weight: root.active ? Font.DemiBold : Font.Normal
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        Rectangle {
            visible: root.detail !== ""
            width: 8; height: 8; radius: 4
            color: Theme.accent
            SequentialAnimation on opacity {
                running: root.detail !== ""
                loops: Animation.Infinite
                NumberAnimation { from: 1; to: 0.25; duration: 700; easing.type: Easing.InOutSine }
                NumberAnimation { from: 0.25; to: 1; duration: 700; easing.type: Easing.InOutSine }
            }
        }
        Text {
            visible: root.badge !== "" && !root.compact
            text: root.badge
            color: Theme.secondary(0.6)
            font.pixelSize: 12
            font.features: ({ "tnum": 1 })
        }
    }

    ToolTip.visible: root.compact && mouse.containsMouse
    ToolTip.text: root.label
    ToolTip.delay: 300

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
