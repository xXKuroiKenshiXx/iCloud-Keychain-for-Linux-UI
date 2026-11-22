import QtQuick
import QtQuick.Controls.Basic

// Inset glass text field.
TextField {
    id: field
    property string leading: ""
    implicitHeight: 42
    color: "#f4f7ff"
    placeholderTextColor: Qt.rgba(0.86, 0.9, 1, 0.48)
    selectionColor: "#3d7fe6"
    selectedTextColor: "white"
    font.pixelSize: 14
    leftPadding: leading ? 38 : 14
    rightPadding: 14
    verticalAlignment: TextInput.AlignVCenter

    background: Rectangle {
        radius: 12
        color: Qt.rgba(0, 0.02, 0.08, field.activeFocus ? 0.42 : 0.30)
        border.width: field.activeFocus ? 1.5 : 1
        border.color: field.activeFocus ? "#78b0ff" : Qt.rgba(1, 1, 1, 0.14)
        Behavior on border.color { ColorAnimation { duration: 160 } }
        Icon {
            visible: field.leading !== ""
            name: field.leading
            size: 16
            color: Qt.rgba(0.86, 0.9, 1, 0.6)
            anchors.left: parent.left
            anchors.leftMargin: 13
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
