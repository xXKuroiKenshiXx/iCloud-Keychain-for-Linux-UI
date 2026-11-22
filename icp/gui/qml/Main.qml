import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    width: 1240
    height: 800
    minimumWidth: 980
    minimumHeight: 640
    visible: true
    title: "Passwords"
    color: "#05070d"
    font.family: "Noto Sans"

    property string section: "all"          // all | codes | wifi | account | settings
    property var selected: null
    property string query: ""
    readonly property bool vaultSection: section === "all" || section === "codes" || section === "wifi"
    readonly property bool needsSignIn: icp.items.length === 0 && !icp.signedIn

    function isWifi(item) { return /wi-?fi|airport/i.test(item.domain || "") || (!item.site && !item.username && item.title !== "") }
    function matches(item) {
        if (section === "codes" && !item.totp) return false
        if (section === "wifi" && !isWifi(item)) return false
        if (section === "all" && isWifi(item)) return false
        if (!query) return true
        var q = query.toLowerCase()
        return (item.name + " " + item.site + " " + item.username).toLowerCase().indexOf(q) >= 0
    }
    function count(kind) {
        var n = 0
        for (var i = 0; i < icp.items.length; i++) {
            var it = icp.items[i]
            if (kind === "codes" ? !!it.totp : kind === "wifi" ? isWifi(it) : !isWifi(it)) n++
        }
        return n
    }
    readonly property var visibleItems: {
        icp.items; section; query
        return icp.items.filter(matches)
    }

    Connections {
        target: icp
        function onToast(message) { toast.show(message) }
        function onPromptChanged() { if (icp.prompt.kind !== "") win.section = "account" }
        function onVaultChanged() {
            win.selected = null
            if (icp.items.length > 0 && win.section === "account" && icp.stage === "done") win.section = "all"
        }
    }

    Backdrop { id: backdrop; anchors.fill: parent }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 14

        // ---------------------------------------------------------------- sidebar
        Glass {
            id: sidebar
            backdrop: backdrop
            Layout.preferredWidth: 240
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 4

                RowLayout {
                    Layout.topMargin: 6
                    Layout.leftMargin: 6
                    Layout.bottomMargin: 10
                    spacing: 10
                    Rectangle {
                        width: 30; height: 30; radius: 8
                        gradient: Gradient {
                            GradientStop { position: 0; color: "#6db2ff" }
                            GradientStop { position: 1; color: "#2f6fe8" }
                        }
                        Icon { anchors.centerIn: parent; name: "key"; size: 17; color: "white"; stroke: 2 }
                    }
                    Text { text: "Passwords"; color: "white"; font.pixelSize: 19; font.weight: Font.Bold }
                }

                Field {
                    id: search
                    Layout.fillWidth: true
                    implicitHeight: 36
                    leading: "search"
                    placeholderText: "Search"
                    enabled: !win.needsSignIn
                    onTextChanged: { win.query = text; if (!win.vaultSection) win.section = "all" }
                }
                Item { height: 10 }

                Repeater {
                    model: [
                        { key: "all", label: "All", icon: "grid" },
                        { key: "codes", label: "Codes", icon: "clock" },
                        { key: "wifi", label: "Wi-Fi", icon: "wifi" }
                    ]
                    delegate: SidebarRow {
                        required property var modelData
                        Layout.fillWidth: true
                        label: modelData.label
                        icon: modelData.icon
                        badge: icp.items.length ? String(win.count(modelData.key)) : ""
                        active: win.section === modelData.key
                        onClicked: { win.section = modelData.key; win.selected = null }
                    }
                }

                Item { Layout.fillHeight: true }

                SidebarRow {
                    Layout.fillWidth: true
                    label: icp.signedIn ? "Apple Account" : "Sign In"
                    icon: "person"
                    detail: icp.busy ? "Working…" : ""
                    active: win.section === "account"
                    onClicked: win.section = "account"
                }
                SidebarRow {
                    Layout.fillWidth: true
                    label: "Settings"
                    icon: "sliders"
                    active: win.section === "settings"
                    onClicked: win.section = "settings"
                }
            }
        }

        // ---------------------------------------------------------------- content
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Vault: list + detail
            RowLayout {
                anchors.fill: parent
                spacing: 14
                visible: win.vaultSection && !win.needsSignIn

                Glass {
                    backdrop: backdrop
                    Layout.preferredWidth: 340
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.margins: 10
                            Text {
                                text: win.section === "codes" ? "Codes" : win.section === "wifi" ? "Wi-Fi" : "All Passwords"
                                color: "white"; font.pixelSize: 22; font.weight: Font.Bold
                                Layout.fillWidth: true
                            }
                            GlassButton {
                                compact: true
                                icon: "sync"
                                text: icp.busy ? "Syncing" : "Sync"
                                enabled: !icp.busy && icp.signedIn
                                onClicked: icp.sync()
                            }
                        }

                        ListView {
                            id: list
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            spacing: 2
                            model: win.visibleItems
                            boundsBehavior: Flickable.StopAtBounds
                            ScrollBar.vertical: ScrollBar {
                                policy: ScrollBar.AsNeeded
                                contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Qt.rgba(1, 1, 1, 0.28) }
                            }
                            delegate: Rectangle {
                                required property var modelData
                                width: ListView.view.width - 8
                                height: 56
                                radius: 12
                                readonly property bool current: win.selected === modelData
                                color: current ? Qt.rgba(0.45, 0.65, 1, 0.30)
                                               : (rowMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.07) : "transparent")
                                Behavior on color { ColorAnimation { duration: 120 } }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 12
                                    spacing: 12
                                    Monogram { label: modelData.site || modelData.name; size: 36 }
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2
                                        Text {
                                            text: modelData.name
                                            color: "white"; font.pixelSize: 14; font.weight: Font.DemiBold
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                        Text {
                                            text: modelData.username || "No user name"
                                            color: Qt.rgba(0.86, 0.9, 1, 0.62); font.pixelSize: 12 + 1
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                    }
                                    Icon { visible: !!modelData.totp; name: "clock"; size: 14; color: Qt.rgba(0.86, 0.9, 1, 0.6) }
                                }
                                MouseArea {
                                    id: rowMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: win.selected = modelData
                                }
                            }

                            Text {
                                anchors.centerIn: parent
                                visible: list.count === 0
                                width: parent.width - 40
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                                text: win.query ? "No results for “" + win.query + "”" : "Nothing here yet"
                                color: Qt.rgba(0.86, 0.9, 1, 0.55); font.pixelSize: 13 + 1
                            }
                        }
                    }
                }

                Glass {
                    backdrop: backdrop
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    DetailPane {
                        anchors.fill: parent
                        entry: win.selected
                        onCopyRequested: (text) => icp.copy(text)
                    }
                }
            }

            // Sign-in / account
            Item {
                anchors.fill: parent
                visible: win.section === "account" || (win.vaultSection && win.needsSignIn)
                SignInCard {
                    anchors.centerIn: parent
                    width: Math.min(parent.width - 40, 470)
                    backdrop: backdrop
                    onFinished: win.section = "all"
                }
            }

            // Settings + debug console
            SettingsPage {
                anchors.fill: parent
                visible: win.section === "settings"
                backdrop: backdrop
            }
        }
    }

    // ---------------------------------------------------------------- toast
    Item {
        id: toast
        property string message: ""
        function show(text) { message = text; state = "shown"; hideTimer.restart() }
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height - 70
        width: toastRow.implicitWidth + 36
        height: 40
        opacity: 0
        states: State { name: "shown"; PropertyChanges { target: toast; opacity: 1; y: win.height - 84 } }
        transitions: Transition { NumberAnimation { properties: "opacity,y"; duration: 260; easing.type: Easing.OutCubic } }
        Timer { id: hideTimer; interval: 2600; onTriggered: toast.state = "" }
        Glass { anchors.fill: parent; backdrop: backdrop; radius: 20; tintTop: 0.22; tintBottom: 0.12 }
        Row {
            id: toastRow
            anchors.centerIn: parent
            spacing: 8
            Icon { name: "check"; size: 15; color: "#7ee0a6"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: toast.message; color: "white"; font.pixelSize: 13; anchors.verticalCenter: parent.verticalCenter }
        }
    }
}
