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

        Text { text: icp.tr("Settings", icp.languageRevision); color: "white"; font.pixelSize: 26; font.weight: Font.Bold }

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
                InfoRow { icon: "globe"; title: icp.tr("Anisette service", icp.languageRevision); value: icp.anisetteUrl }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                InfoRow { icon: "folder"; title: icp.tr("Session and vault", icp.languageRevision); value: icp.dataDir }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 14
                    spacing: 14
                    Icon { name: "globe"; size: 20; color: "#8ec2ff" }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text { text: icp.tr("Website icons and names", icp.languageRevision); color: "white"; font.pixelSize: 14 }
                        Text {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: icp.tr("Fetched directly from each saved site over HTTPS, never through an icon service, and stored encrypted on this computer.", icp.languageRevision)
                            color: Qt.rgba(0.86, 0.9, 1, 0.6); font.pixelSize: 12
                        }
                    }
                    GlassButton { compact: true; icon: "sync"; text: icp.tr("Refresh", icp.languageRevision); enabled: icp.fetchIcons; onClicked: icp.refreshIcons() }
                    Toggle { checked: icp.fetchIcons; onToggled: (on) => icp.setFetchIcons(on) }
                }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 14
                    spacing: 14
                    Icon { name: "globe"; size: 20; color: "#8ec2ff" }
                    Text { text: icp.tr("Language", icp.languageRevision); color: "white"; font.pixelSize: 14; Layout.fillWidth: true }
                    GlassButton {
                        id: languageButton
                        compact: true
                        icon: "chevron"
                        text: {
                            var options = icp.languageOptions
                            for (var i = 0; i < options.length; i++)
                                if (options[i].code === icp.languagePreference) return options[i].name
                            return options[0].name
                        }
                        onClicked: languageMenu.open()
                        Popup {
                            id: languageMenu
                            y: languageButton.height + 6
                            x: languageButton.width - width
                            width: 230
                            padding: 6
                            modal: false
                            focus: true
                            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
                            enter: Transition { ParallelAnimation {
                                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180; easing.type: Easing.OutCubic }
                                NumberAnimation { property: "scale"; from: 0.94; to: 1; duration: 260; easing.type: Easing.OutBack }
                            } }
                            exit: Transition { NumberAnimation { property: "opacity"; to: 0; duration: 120 } }
                            background: Rectangle {
                                radius: 14
                                color: Qt.rgba(0.07, 0.1, 0.18, 0.96)
                                border.width: 1
                                border.color: Qt.rgba(1, 1, 1, 0.18)
                            }
                            contentItem: Column {
                                spacing: 2
                                Repeater {
                                    model: icp.languageOptions
                                    delegate: Rectangle {
                                        id: option
                                        required property var modelData
                                        width: 218
                                        height: 34
                                        radius: 9
                                        color: optionMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.10) : "transparent"
                                        Row {
                                            anchors.verticalCenter: parent.verticalCenter
                                            anchors.left: parent.left
                                            anchors.leftMargin: 10
                                            spacing: 8
                                            Icon {
                                                name: "check"; size: 14; color: "#8ec2ff"
                                                opacity: option.modelData.code === icp.languagePreference ? 1 : 0
                                                anchors.verticalCenter: parent.verticalCenter
                                            }
                                            Text {
                                                text: option.modelData.name
                                                color: "white"; font.pixelSize: 13
                                                anchors.verticalCenter: parent.verticalCenter
                                            }
                                        }
                                        MouseArea {
                                            id: optionMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: { icp.setLanguage(option.modelData.code); languageMenu.close() }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 50; implicitHeight: 1; color: Qt.rgba(1, 1, 1, 0.08) }
                InfoRow { icon: "person"; title: icp.tr("Status", icp.languageRevision); value: icp.busy ? icp.status : (icp.signedIn ? icp.tr("Signed in · {n} passwords", icp.languageRevision).replace("{n}", icp.items.length) : icp.tr("Not signed in", icp.languageRevision)) }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 6
            spacing: 10
            Icon { name: "terminal"; size: 18; color: "#8ec2ff" }
            Text { text: icp.tr("Debug console", icp.languageRevision); color: "white"; font.pixelSize: 16; font.weight: Font.DemiBold; Layout.fillWidth: true }
            GlassButton {
                compact: true
                text: root.follow ? icp.tr("Following", icp.languageRevision) : icp.tr("Follow", icp.languageRevision)
                onClicked: { root.follow = !root.follow; if (root.follow) console_.positionViewAtEnd() }
            }
            GlassButton { compact: true; icon: "copy"; text: icp.tr("Copy Log", icp.languageRevision); onClicked: icp.copyLog() }
            GlassButton { compact: true; text: icp.tr("Clear", icp.languageRevision); onClicked: icp.clearLog() }
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
                    text: icp.tr("Engine activity appears here step by step.", icp.languageRevision)
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
