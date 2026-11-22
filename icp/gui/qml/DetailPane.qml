import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs

// Detail of one saved login, laid out like an inset grouped list.
Item {
    id: root
    property var entry: null
    property bool revealed: false
    property var code: ({})
    signal copyRequested(string text)
    readonly property string shownName: entry ? icp.displayName(entry.iconKey, entry.name, entry.title || "", icp.iconRevision) : ""

    onEntryChanged: { revealed = false; refreshCode(); if (entry && icp.animations) detailIn.restart() }

    ParallelAnimation {
        id: detailIn
        NumberAnimation { target: column; property: "opacity"; from: 0; to: 1; duration: 300; easing.type: Easing.OutCubic }
        NumberAnimation { target: detailLift; property: "y"; from: 12; to: 0; duration: 460; easing.type: Easing.OutExpo }
    }
    function refreshCode() { code = entry && entry.totp ? icp.totp(entry.totp) : ({}) }
    function grouped(c) { return c && c.length === 6 ? c.slice(0, 3) + " " + c.slice(3) : (c || "") }

    Timer {
        interval: 1000; repeat: true
        running: root.visible && !!root.entry && !!root.entry.totp
        onTriggered: root.refreshCode()
    }
    FileDialog {
        id: iconDialog
        title: icp.tr("Choose an icon", icp.languageRevision)
        nameFilters: [icp.tr("Images", icp.languageRevision) + " (*.png *.jpg *.jpeg *.webp *.ico *.bmp)"]
        onAccepted: if (root.entry) icp.chooseIcon(root.entry.iconKey, root.shownName, selectedFile.toString())
    }
    Timer { id: hideTimer; interval: 20000; onTriggered: root.revealed = false }

    // Empty state
    ColumnLayout {
        anchors.centerIn: parent
        visible: !root.entry
        spacing: 12
        Icon { Layout.alignment: Qt.AlignHCenter; name: "lock"; size: 44; stroke: 1.4; color: Theme.secondary(0.45) }
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: icp.tr("Select a password", icp.languageRevision)
            color: Theme.secondary(0.75); font.pixelSize: 17; font.weight: Font.DemiBold
        }
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: icp.tr("{n} passwords in your iCloud Keychain", icp.languageRevision).replace("{n}", icp.items.length)
            color: Theme.secondary(0.5); font.pixelSize: 13
        }
    }

    Flickable {
        anchors.fill: parent
        anchors.margins: 28
        visible: !!root.entry
        contentHeight: column.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        ColumnLayout {
            id: column
            width: parent.width
            transform: Translate { id: detailLift }
            spacing: 22

            RowLayout {
                spacing: 16
                Monogram { label: root.shownName; source: root.entry ? icp.iconSource(root.entry.iconKey, icp.iconRevision) : ""; size: 64 }
                ColumnLayout {
                    spacing: 6
                    Text {
                        text: root.shownName
                        textFormat: Text.PlainText
                        color: Theme.text; font.pixelSize: 26; font.weight: Font.Bold
                        elide: Text.ElideRight; Layout.maximumWidth: column.width - 90
                    }
                    Row {
                        spacing: 6
                        GlassButton { compact: true; text: icp.tr("Change Icon…", icp.languageRevision); onClicked: iconDialog.open() }
                        GlassButton {
                            compact: true; text: icp.tr("Reset Icon", icp.languageRevision)
                            visible: root.entry && icp.isCustomIcon(root.entry.iconKey, icp.iconRevision)
                            onClicked: icp.resetIcon(root.entry.iconKey, root.entry.site || "")
                        }
                    }
                    Text {
                        visible: root.entry && root.entry.group
                        text: root.entry ? icp.tr("Shared group · {g}", icp.languageRevision).replace("{g}", root.entry.group) : ""
                        textFormat: Text.PlainText
                        color: Theme.secondary(0.6); font.pixelSize: 13
                    }
                }
            }

            // Grouped fields
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: fields.implicitHeight
                radius: 16
                color: Theme.inset(0.28)
                border.width: 1
                border.color: Theme.overlay(0.10)

                ColumnLayout {
                    id: fields
                    width: parent.width
                    spacing: 0

                    FieldRow {
                        title: icp.tr("User name", icp.languageRevision)
                        value: root.entry ? (root.entry.username || "—") : ""
                        copyable: root.entry && !!root.entry.username
                        onCopy: root.copyRequested(root.entry.username)
                    }
                    Divider {}
                    FieldRow {
                        title: icp.tr("Password", icp.languageRevision)
                        value: root.entry ? (root.revealed ? root.entry.password : "••••••••••••") : ""
                        mono: root.revealed
                        copyable: true
                        extraIcon: root.revealed ? "eyeoff" : "eye"
                        onExtra: { root.revealed = !root.revealed; if (root.revealed) hideTimer.restart() }
                        onCopy: root.copyRequested(root.entry.password)
                    }
                    Divider { visible: !!root.code.code }
                    FieldRow {
                        visible: !!root.code.code
                        title: icp.tr("Verification code", icp.languageRevision)
                        value: root.grouped(root.code.code)
                        mono: true
                        trailing: root.code.expires ? Math.max(0, Math.round(root.code.expires - Date.now() / 1000)) + "s" : ""
                        copyable: true
                        onCopy: root.copyRequested(root.code.code)
                    }
                    Divider { visible: root.entry && !!root.entry.site }
                    FieldRow {
                        visible: root.entry && !!root.entry.site
                        title: icp.tr("Website", icp.languageRevision)
                        value: root.entry ? root.entry.site : ""
                        valueColor: Theme.accent
                        copyable: true
                        onCopy: root.copyRequested(root.entry.site)
                    }
                }
            }

            ColumnLayout {
                visible: root.entry && !!root.entry.notes
                Layout.fillWidth: true
                spacing: 8
                Text { text: icp.tr("Notes", icp.languageRevision); color: Theme.secondary(0.6); font.pixelSize: 12 + 1; font.weight: Font.DemiBold }
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: notes.implicitHeight + 28
                    radius: 16
                    color: Theme.inset(0.28)
                    border.width: 1
                    border.color: Theme.overlay(0.10)
                    Text {
                        id: notes
                        anchors.fill: parent
                        anchors.margins: 14
                        text: root.entry ? (root.entry.notes || "") : ""
                        color: Theme.text; font.pixelSize: 13 + 1
                        wrapMode: Text.Wrap
                        textFormat: Text.PlainText
                    }
                }
            }
        }
    }

    component Divider: Rectangle {
        Layout.fillWidth: true
        Layout.leftMargin: 16
        implicitHeight: 1
        color: Theme.overlay(0.08)
    }

    component FieldRow: Item {
        id: fieldRow
        property string title
        property string value
        property string trailing: ""
        property string extraIcon: ""
        property bool copyable: false
        property bool mono: false
        property color valueColor: Theme.text
        signal copy()
        signal extra()
        Layout.fillWidth: true
        implicitHeight: 64

        ColumnLayout {
            anchors.left: parent.left
            anchors.right: actions.left
            anchors.leftMargin: 16
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3
            Text { text: fieldRow.title; color: Theme.secondary(0.58); font.pixelSize: 12 }
            Text {
                text: fieldRow.value
                color: fieldRow.valueColor
                font.pixelSize: fieldRow.mono ? 16 : 15
                font.family: fieldRow.mono ? "DejaVu Sans Mono" : "Noto Sans"
                font.letterSpacing: fieldRow.mono ? 0.5 : 0
                elide: Text.ElideRight
                Layout.fillWidth: true
                textFormat: Text.PlainText
            }
        }
        Row {
            id: actions
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6
            Text {
                visible: fieldRow.trailing !== ""
                text: fieldRow.trailing
                color: Theme.secondary(0.55); font.pixelSize: 12
                font.features: ({ "tnum": 1 })
                anchors.verticalCenter: parent.verticalCenter
            }
            GlassButton {
                visible: fieldRow.extraIcon !== ""
                compact: true; icon: fieldRow.extraIcon
                onClicked: fieldRow.extra()
            }
            GlassButton {
                visible: fieldRow.copyable
                compact: true; icon: "copy"; text: icp.tr("Copy", icp.languageRevision)
                onClicked: fieldRow.copy()
            }
        }
    }
}
