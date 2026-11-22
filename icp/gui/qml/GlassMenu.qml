import QtQuick
import QtQuick.Controls.Basic

// A small frosted menu. `entries` is a list of { text, checked, separator, enabled };
// `picked(index)` fires when one is chosen.
Popup {
    id: menu
    property var entries: []
    signal picked(int index)

    width: 230
    padding: 6
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    enter: Transition {
        enabled: icp.animations
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 160; easing.type: Easing.OutCubic }
            NumberAnimation { property: "scale"; from: 0.94; to: 1; duration: 240; easing.type: Easing.OutBack }
        }
    }
    exit: Transition { enabled: icp.animations; NumberAnimation { property: "opacity"; to: 0; duration: 110 } }
    background: Rectangle {
        radius: 14
        color: Theme.popup
        border.width: 1
        border.color: Theme.overlay(0.18)
    }
    contentItem: Column {
        spacing: 2
        Repeater {
            model: menu.entries
            delegate: Item {
                id: entry
                required property var modelData
                required property int index
                width: menu.width - menu.padding * 2
                height: modelData.separator ? 9 : 34
                Rectangle {
                    visible: entry.modelData.separator === true
                    anchors.centerIn: parent
                    width: parent.width - 16
                    height: 1
                    color: Theme.overlay(0.12)
                }
                Rectangle {
                    visible: !entry.modelData.separator
                    anchors.fill: parent
                    radius: 9
                    color: entryMouse.containsMouse && entry.modelData.enabled !== false ? Theme.overlay(0.10) : "transparent"
                    Row {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        spacing: 8
                        Icon {
                            name: entry.modelData.icon || "check"
                            size: 14
                            color: Theme.accent
                            opacity: entry.modelData.icon ? 1 : (entry.modelData.checked ? 1 : 0)
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: entry.modelData.text || ""
                            color: entry.modelData.enabled === false ? Theme.overlay(0.35) : Theme.text
                            font.pixelSize: 13
                            elide: Text.ElideRight
                            width: menu.width - 60
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    MouseArea {
                        id: entryMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: entry.modelData.enabled !== false
                        cursorShape: Qt.PointingHandCursor
                        onClicked: { menu.picked(entry.index); menu.close() }
                    }
                }
            }
        }
    }
}
