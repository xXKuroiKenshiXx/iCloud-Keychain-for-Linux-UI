import QtQuick
import QtQuick.Controls.Basic

// Inset glass text field. `secret` hides the text and adds an eye button to show it.
TextField {
    id: field
    property string leading: ""
    property bool secret: false
    property bool shown: false
    implicitHeight: 42
    color: "#f4f7ff"
    placeholderTextColor: Qt.rgba(0.86, 0.9, 1, 0.48)
    selectionColor: "#3d7fe6"
    selectedTextColor: "white"
    font.pixelSize: 14
    leftPadding: leading ? 38 : 14
    rightPadding: secret ? 42 : 14
    verticalAlignment: TextInput.AlignVCenter
    echoMode: secret && !shown ? TextInput.Password : TextInput.Normal
    inputMethodHints: secret ? (Qt.ImhSensitiveData | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase) : Qt.ImhNone
    onSecretChanged: shown = false
    onActiveFocusChanged: if (!activeFocus) shown = false

    background: Rectangle {
        radius: 12
        color: Qt.rgba(0, 0.02, 0.08, field.activeFocus ? 0.42 : 0.30)
        border.width: field.activeFocus ? 1.5 : 1
        border.color: field.activeFocus ? "#78b0ff" : Qt.rgba(1, 1, 1, 0.14)
        Behavior on border.color { enabled: icp.animations; ColorAnimation { duration: 160 } }
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

    Item {
        visible: field.secret
        width: 34
        height: 34
        anchors.right: parent.right
        anchors.rightMargin: 5
        anchors.verticalCenter: parent.verticalCenter
        Rectangle {
            anchors.fill: parent
            radius: 10
            color: eyeMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.10) : "transparent"
        }
        Icon {
            anchors.centerIn: parent
            name: field.shown ? "eyeoff" : "eye"
            size: 17
            color: field.shown ? "#8ec2ff" : Qt.rgba(0.86, 0.9, 1, 0.7)
        }
        MouseArea {
            id: eyeMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: { field.shown = !field.shown; field.forceActiveFocus() }
        }
    }
}
