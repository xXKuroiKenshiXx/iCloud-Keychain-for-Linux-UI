import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

// Settings: connection, storage, and the live debug console.
Glass {
    id: root
    property bool follow: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 18

        Text { text: "Settings"; color: "white"; font.pixelSize: 26; font.weight: Font.Bold }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: info.implicitHeight
            radius: 16
            color: Qt.rgba(0, 0.02, 0.08, 0.28)
            border.width: 1
            border.color: Qt.rgba(1, 1, 1, 0.10)
            ColumnLayout {
                id: info
                width: parent.width
                spacing: 0
                InfoRow { icon: "globe"; title: "Anisette service"; value: icp.anisetteUrl }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                InfoRow { icon: "folder"; title: "Session and vault"; value: icp.dataDir }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 14
                    spacing: 14
                    Icon { name: "globe"; size: 20; color: "#8ec2ff" }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text { text: "Website icons and names"; color: "white"; font.pixelSize: 14 }
                        Text {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: "Fetched directly from each saved site over HTTPS, never through an icon service, and stored encrypted on this computer."
                            color: Qt.rgba(0.86, 0.9, 1, 0.6); font.pixelSize: 12
                        }
                    }
                    GlassButton { compact: true; icon: "sync"; text: "Refresh"; enabled: icp.fetchIcons; onClicked: icp.refreshIcons() }
                    Toggle { checked: icp.fetchIcons; onToggled: (on) => icp.setFetchIcons(on) }
                }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                InfoRow { icon: "person"; title: "Status"; value: icp.busy ? icp.status : (icp.signedIn ? "Signed in · " + icp.items.length + " passwords" : "Not signed in") }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 6
            spacing: 10
            Icon { name: "terminal"; size: 18; color: "#8ec2ff" }
            Text { text: "Debug console"; color: "white"; font.pixelSize: 16; font.weight: Font.DemiBold; Layout.fillWidth: true }
            GlassButton {
                compact: true
                text: root.follow ? "Following" : "Follow"
                onClicked: { root.follow = !root.follow; if (root.follow) console_.positionViewAtEnd() }
            }
            GlassButton { compact: true; icon: "copy"; text: "Copy Log"; onClicked: icp.copyLog() }
            GlassButton { compact: true; text: "Clear"; onClicked: icp.clearLog() }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 16
            color: Qt.rgba(0, 0.01, 0.05, 0.55)
            border.width: 1
            border.color: Qt.rgba(1, 1, 1, 0.10)

            ListView {
                id: console_
                anchors.fill: parent
                anchors.margins: 12
                clip: true
                model: icp.log
                boundsBehavior: Flickable.StopAtBounds
                onCountChanged: if (root.follow) Qt.callLater(positionViewAtEnd)
                ScrollBar.vertical: ScrollBar {
                    contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Qt.rgba(1, 1, 1, 0.28) }
                }
                delegate: Text {
                    required property var modelData
                    width: ListView.view.width - 10
                    wrapMode: Text.WrapAnywhere
                    textFormat: Text.PlainText
                    font.family: "DejaVu Sans Mono"
                    font.pixelSize: 12
                    lineHeight: 1.15
                    color: modelData.level === "error" ? "#ff9b9b"
                         : modelData.level === "warning" ? "#ffd27a"
                         : modelData.level === "debug" ? Qt.rgba(0.8, 0.86, 1, 0.5)
                         : "#d6e4ff"
                    text: modelData.time + "  " + modelData.text
                }
                Text {
                    anchors.centerIn: parent
                    visible: console_.count === 0
                    text: "Engine activity appears here step by step."
                    color: Qt.rgba(0.86, 0.9, 1, 0.45); font.pixelSize: 13
                }
            }
        }
    }

    component Toggle: Rectangle {
        id: toggle
        property bool checked: false
        signal toggled(bool on)
        implicitWidth: 46
        implicitHeight: 28
        radius: 14
        color: checked ? "#3a8bff" : Qt.rgba(1, 1, 1, 0.16)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.25)
        Behavior on color { ColorAnimation { duration: 160 } }
        Rectangle {
            width: 22; height: 22; radius: 11
            y: 3
            x: toggle.checked ? toggle.width - width - 3 : 3
            color: "white"
            Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: toggle.toggled(!toggle.checked) }
    }

    component InfoRow: RowLayout {
        property string icon
        property string title
        property string value
        Layout.fillWidth: true
        Layout.margins: 14
        spacing: 14
        Icon { name: parent.icon; size: 20; color: "#8ec2ff" }
        Text { text: parent.title; color: "white"; font.pixelSize: 14; Layout.preferredWidth: 150 }
        Text {
            text: parent.value
            color: Qt.rgba(0.86, 0.9, 1, 0.7); font.pixelSize: 13
            elide: Text.ElideMiddle; Layout.fillWidth: true
            horizontalAlignment: Text.AlignRight
            textFormat: Text.PlainText
        }
    }
}
