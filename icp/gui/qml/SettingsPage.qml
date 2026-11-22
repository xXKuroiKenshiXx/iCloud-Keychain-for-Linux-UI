import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

// Settings, grouped in sections whose rows share one layout: icon, title with an optional
// description, and the controls aligned on the right. The debug console closes the page.
Glass {
    id: root
    property bool follow: true
    signal requestSetup()
    function tt(text) { return icp.tr(text, icp.languageRevision) }

    Flickable {
        anchors.fill: parent
        anchors.margins: 28
        contentHeight: page.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar { contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Theme.overlay(0.28) } }

        ColumnLayout {
            id: page
            width: parent.width
            spacing: 22

            Text { text: root.tt("Settings"); color: Theme.text; font.pixelSize: 26; font.weight: Font.Bold }

            // ---------------------------------------------------------- connection
            Section {
                title: root.tt("Connection")
                SettingRow {
                    icon: "globe"
                    title: root.tt("Anisette service")
                    detail: icp.anisetteUrl
                    Rectangle {
                        width: 9; height: 9; radius: 4.5
                        anchors.verticalCenter: parent.verticalCenter
                        color: icp.anisetteState === 1 ? "#5fd68e" : icp.anisetteState === 0 ? "#ff7a7a" : "#ffbe5c"
                    }
                    GlassButton { compact: true; text: root.tt("Set Up…"); onClicked: root.requestSetup() }
                }
                SettingRow {
                    visible: icp.runningAppImage || icp.inAppMenu
                    icon: "grid"
                    title: root.tt("Applications menu")
                    GlassButton {
                        compact: true
                        prominent: !icp.inAppMenu
                        text: icp.inAppMenu ? root.tt("Remove") : root.tt("Add")
                        onClicked: icp.inAppMenu ? icp.removeFromAppMenu() : icp.addToAppMenu()
                    }
                }
                SettingRow {
                    last: true
                    icon: "person"
                    title: root.tt("Status")
                    detail: icp.busy ? icp.status : (icp.signedIn ? root.tt("Signed in · {n} passwords").replace("{n}", icp.items.length) : root.tt("Not signed in"))
                }
            }

            // ---------------------------------------------------------- interface
            Section {
                title: root.tt("Interface")
                SettingRow {
                    icon: "globe"
                    title: root.tt("Language")
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
                        GlassMenu {
                            id: languageMenu
                            y: languageButton.height + 6
                            x: languageButton.width - width
                            entries: {
                                var out = []
                                var options = icp.languageOptions
                                for (var i = 0; i < options.length; i++)
                                    out.push({ text: options[i].name, checked: options[i].code === icp.languagePreference })
                                return out
                            }
                            onPicked: (index) => icp.setLanguage(icp.languageOptions[index].code)
                        }
                    }
                }
                SettingRow {
                    icon: "eye"
                    title: root.tt("Appearance")
                    Segmented {
                        options: [{ key: "system", label: root.tt("System") }, { key: "light", label: root.tt("Light") }, { key: "dark", label: root.tt("Dark") }]
                        current: icp.appearance
                        onPicked: (key) => icp.setAppearance(key)
                    }
                }
                SettingRow {
                    icon: "sidebar"
                    title: root.tt("Sidebar")
                    Segmented {
                        options: [{ key: "full", label: root.tt("Full") }, { key: "compact", label: root.tt("Compact") }]
                        current: icp.sidebarStyle
                        onPicked: (key) => icp.setSidebarMode(key)
                    }
                }
                SettingRow {
                    last: true
                    icon: "wand"
                    title: root.tt("Animations and effects")
                    Toggle { checked: icp.animations; onToggled: (on) => icp.setAnimations(on) }
                }
            }

            // ---------------------------------------------------------- data
            Section {
                title: root.tt("Data")
                SettingRow {
                    icon: "globe"
                    title: root.tt("Website icons and names")
                    detail: root.tt("Fetched directly from each saved site over HTTPS, never through an icon service, and stored encrypted on this computer.")
                    GlassButton {
                        compact: true
                        icon: "sync"
                        implicitWidth: implicitHeight
                        enabled: icp.fetchIcons
                        onClicked: icp.refreshIcons()
                        ToolTip.visible: refreshHover.hovered
                        ToolTip.delay: 300
                        ToolTip.text: root.tt("Refresh")
                        HoverHandler { id: refreshHover }
                    }
                    GlassButton {
                        compact: true
                        icon: "trash"
                        implicitWidth: implicitHeight
                        onClicked: icp.clearIconCache()
                        ToolTip.visible: trashHover.hovered
                        ToolTip.delay: 300
                        ToolTip.text: root.tt("Clear Icon Cache")
                        HoverHandler { id: trashHover }
                    }
                    Toggle { checked: icp.fetchIcons; onToggled: (on) => icp.setFetchIcons(on) }
                }
                SettingRow {
                    last: true
                    icon: "folder"
                    title: root.tt("Session and vault")
                    detail: icp.dataDir
                }
            }

            // ---------------------------------------------------------- debug console
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Text { text: root.tt("Debug console"); color: Theme.secondary(0.6); font.pixelSize: 12; font.weight: Font.DemiBold; font.capitalization: Font.AllUppercase; font.letterSpacing: 0.6; Layout.fillWidth: true; elide: Text.ElideRight }
                GlassButton {
                    compact: true
                    text: root.follow ? root.tt("Following") : root.tt("Follow")
                    onClicked: { root.follow = !root.follow; if (root.follow) console_.positionViewAtEnd() }
                }
                GlassButton { compact: true; icon: "copy"; text: root.tt("Copy Log"); onClicked: icp.copyLog() }
                GlassButton { compact: true; icon: "trash"; text: root.tt("Clear"); onClicked: icp.clearLog() }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 300
                radius: 16
                color: Theme.inset(0.55)
                border.width: 1
                border.color: Theme.overlay(0.10)

                ListView {
                    id: console_
                    anchors.fill: parent
                    anchors.margins: 12
                    clip: true
                    model: icp.log
                    boundsBehavior: Flickable.StopAtBounds
                    onCountChanged: if (root.follow) Qt.callLater(positionViewAtEnd)
                    ScrollBar.vertical: ScrollBar {
                        contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Theme.overlay(0.28) }
                    }
                    delegate: Text {
                        required property var modelData
                        width: ListView.view.width - 10
                        wrapMode: Text.WrapAnywhere
                        textFormat: Text.PlainText
                        font.family: "DejaVu Sans Mono"
                        font.pixelSize: 12
                        lineHeight: 1.15
                        color: modelData.level === "error" ? (Theme.dark ? "#ff9b9b" : "#b3261e")
                             : modelData.level === "warning" ? (Theme.dark ? "#ffd27a" : "#8a5a00")
                             : modelData.level === "debug" ? Theme.secondary(0.5)
                             : Theme.consoleText
                        text: modelData.time + "  " + modelData.text
                    }
                    Text {
                        anchors.centerIn: parent
                        visible: console_.count === 0
                        text: root.tt("Engine activity appears here step by step.")
                        color: Theme.secondary(0.45); font.pixelSize: 13
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------ building blocks
    component Section: ColumnLayout {
        id: section
        property string title
        default property alias rows: inner.data
        Layout.fillWidth: true
        spacing: 8
        Text {
            text: section.title
            color: Theme.secondary(0.6); font.pixelSize: 12; font.weight: Font.DemiBold
            font.capitalization: Font.AllUppercase; font.letterSpacing: 0.6
            Layout.leftMargin: 4
        }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: inner.implicitHeight
            radius: 16
            color: Theme.inset(0.28)
            border.width: 1
            border.color: Theme.overlay(0.10)
            ColumnLayout { id: inner; width: parent.width; spacing: 0 }
        }
    }

    component SettingRow: Item {
        id: row
        property string icon
        property string title
        property string detail: ""
        property bool last: false
        default property alias controls: controlRow.data
        Layout.fillWidth: true
        implicitHeight: Math.max(58, texts.implicitHeight + 26)

        Icon { id: rowIcon; name: row.icon; size: 20; color: Theme.accent; anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter }
        ColumnLayout {
            id: texts
            anchors.left: rowIcon.right
            anchors.leftMargin: 14
            anchors.right: controlRow.left
            anchors.rightMargin: 14
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2
            Text { Layout.fillWidth: true; text: row.title; color: Theme.text; font.pixelSize: 14; elide: Text.ElideRight }
            Text {
                visible: row.detail !== ""
                Layout.fillWidth: true
                text: row.detail
                textFormat: Text.PlainText
                wrapMode: Text.WordWrap
                maximumLineCount: 3
                elide: Text.ElideRight
                color: Theme.secondary(0.6); font.pixelSize: 12; lineHeight: 1.15
            }
        }
        RowLayout {
            id: controlRow
            anchors.right: parent.right
            anchors.rightMargin: 14
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8
        }
        Rectangle {
            visible: !row.last
            anchors.left: texts.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.overlay(0.08)
        }
    }

    component Segmented: Rectangle {
        id: seg
        property var options: []
        property string current: ""
        signal picked(string key)
        implicitWidth: segRow.implicitWidth + 6
        implicitHeight: 34
        radius: 17
        color: Theme.overlay(0.08)
        border.width: 1
        border.color: Theme.overlay(0.12)
        Row {
            id: segRow
            anchors.centerIn: parent
            spacing: 2
            Repeater {
                model: seg.options
                delegate: Rectangle {
                    id: segItem
                    required property var modelData
                    readonly property bool selected: seg.current === modelData.key
                    width: segLabel.implicitWidth + 22
                    height: 28
                    radius: 14
                    color: selected ? "#3a8bff" : (segMouse.containsMouse ? Theme.overlay(0.10) : "transparent")
                    Behavior on color { enabled: icp.animations; ColorAnimation { duration: 140 } }
                    Text {
                        id: segLabel
                        anchors.centerIn: parent
                        text: segItem.modelData.label
                        color: segItem.selected ? "white" : Theme.text
                        font.pixelSize: 13
                        font.weight: segItem.selected ? Font.DemiBold : Font.Normal
                    }
                    MouseArea { id: segMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: seg.picked(segItem.modelData.key) }
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
        color: checked ? "#3a8bff" : Theme.overlay(0.16)
        border.width: 1
        border.color: Theme.overlay(0.25)
        Behavior on color { enabled: icp.animations; ColorAnimation { duration: 160 } }
        Rectangle {
            width: 22; height: 22; radius: 11
            y: 3
            x: toggle.checked ? toggle.width - width - 3 : 3
            color: "#ffffff"
            Behavior on x { enabled: icp.animations; NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: toggle.toggled(!toggle.checked) }
    }
}
