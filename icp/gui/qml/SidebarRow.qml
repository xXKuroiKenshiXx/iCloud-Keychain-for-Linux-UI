import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    property string label
    property string icon
    property string badge: ""
    property string detail: ""
    property bool active: false
    signal clicked()

    implicitHeight: 38
    radius: 10
    color: active ? Qt.rgba(1, 1, 1, 0.16) : (mouse.containsMouse ? Qt.rgba(1, 1, 1, 0.07) : "transparent")
    Behavior on color { ColorAnimation { duration: 120 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 10
        Icon { name: root.icon; size: 17; color: root.active ? "#8ec2ff" : Qt.rgba(0.88, 0.92, 1, 0.8) }
        Text {
            text: root.label
            color: "white"
            font.pixelSize: 13 + 1
            font.weight: root.active ? Font.DemiBold : Font.Normal
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        Rectangle {
            visible: root.detail !== ""
            width: 8; height: 8; radius: 4
            color: "#8ec2ff"
            SequentialAnimation on opacity {
                running: root.detail !== ""
                loops: Animation.Infinite
                NumberAnimation { from: 1; to: 0.25; duration: 700; easing.type: Easing.InOutSine }
                NumberAnimation { from: 0.25; to: 1; duration: 700; easing.type: Easing.InOutSine }
            }
        }
        Text {
            visible: root.badge !== ""
            text: root.badge
            color: Qt.rgba(0.86, 0.9, 1, 0.6)
            font.pixelSize: 12
            font.features: ({ "tnum": 1 })
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
