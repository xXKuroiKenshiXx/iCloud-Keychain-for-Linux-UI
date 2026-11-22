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
    title: icp.tr("Passwords", icp.languageRevision)
    color: "#05070d"
    font.family: "Noto Sans"

    property string section: "all"          // all | codes | wifi | account | settings
    property var selected: null
    property string query: ""
    readonly property bool vaultSection: section === "all" || section === "codes" || section === "wifi"
    readonly property bool needsSignIn: icp.items.length === 0 && !icp.signedIn
    readonly property bool needsSetup: needsSignIn && icp.anisetteState === 0
    readonly property bool showSetup: section === "setup" || (needsSetup && (vaultSection || section === "account"))

    function isWifi(item) { return /wi-?fi|airport/i.test(item.domain || "") || (!item.site && !item.username && item.title !== "") }
    function matches(item) {
        if (section === "codes" && !item.totp) return false
        if (section === "wifi" && !isWifi(item)) return false
        if (section === "all" && isWifi(item)) return false
        if (!query) return true
        var q = query.toLowerCase()
        return (item.display + " " + item.name + " " + item.site + " " + item.username).toLowerCase().indexOf(q) >= 0
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

    onSelectedChanged: list.syncCurrent()

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

    // Pointer light shared by every glass panel; it trails the cursor for a liquid feel.
    HoverHandler { id: pointer }
    Item {
        id: light
        anchors.fill: parent
        property real px: pointer.point.position.x
        property real py: pointer.point.position.y
        readonly property bool active: pointer.hovered
        Behavior on px { SmoothedAnimation { velocity: 1600; duration: 260 } }
        Behavior on py { SmoothedAnimation { velocity: 1600; duration: 260 } }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 14

        // ---------------------------------------------------------------- sidebar
        Glass {
            id: sidebar
            backdrop: backdrop
            light: light
            revealDelay: 0
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
                    Image {
                        width: 32; height: 32
                        source: "icon.svg"
                        sourceSize.width: 64
                        sourceSize.height: 64
                        smooth: true
                    }
                    Text { text: icp.tr("Passwords", icp.languageRevision); color: "white"; font.pixelSize: 19; font.weight: Font.Bold }
                }

                Field {
                    id: search
                    Layout.fillWidth: true
                    implicitHeight: 36
                    leading: "search"
                    placeholderText: icp.tr("Search", icp.languageRevision)
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
                        label: icp.tr(modelData.label, icp.languageRevision)
                        icon: modelData.icon
                        badge: icp.items.length ? String(win.count(modelData.key)) : ""
                        active: win.section === modelData.key
                        onClicked: { win.section = modelData.key; win.selected = null }
                    }
                }

                Item { Layout.fillHeight: true }

                SidebarRow {
                    Layout.fillWidth: true
                    label: icp.signedIn ? icp.tr("Apple Account", icp.languageRevision) : icp.tr("Sign In", icp.languageRevision)
                    icon: "person"
                    detail: icp.busy ? "•" : ""
                    active: win.section === "account"
                    onClicked: win.section = "account"
                }
                SidebarRow {
                    Layout.fillWidth: true
                    label: icp.tr("Settings", icp.languageRevision)
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
                readonly property bool shown: win.vaultSection && !win.needsSignIn
                opacity: shown ? 1 : 0
                scale: shown ? 1 : 0.985
                visible: opacity > 0.01
                enabled: shown
                Behavior on opacity { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }

                Glass {
                    backdrop: backdrop
                    light: light
                    revealDelay: 90
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
                                text: win.section === "codes" ? icp.tr("Codes", icp.languageRevision) : win.section === "wifi" ? icp.tr("Wi-Fi", icp.languageRevision) : icp.tr("All Passwords", icp.languageRevision)
                                color: "white"; font.pixelSize: 22; font.weight: Font.Bold
                                Layout.fillWidth: true
                                Layout.minimumWidth: 0
                                elide: Text.ElideRight
                                fontSizeMode: Text.HorizontalFit
                                minimumPixelSize: 16
                            }
                            GlassButton {
                                id: syncButton
                                compact: true
                                icon: "sync"
                                implicitWidth: implicitHeight
                                enabled: !icp.busy && icp.signedIn
                                onClicked: icp.sync()
                                RotationAnimation on rotation {
                                    running: icp.busy
                                    from: 0; to: 360; duration: 1100; loops: Animation.Infinite
                                    onStopped: syncButton.rotation = 0
                                }
                                ToolTip.visible: syncHover.hovered
                                ToolTip.delay: 400
                                ToolTip.text: icp.busy ? icp.tr("Syncing", icp.languageRevision) : icp.tr("Sync Now", icp.languageRevision)
                                HoverHandler { id: syncHover }
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
                            currentIndex: -1
                            cacheBuffer: 240
                            reuseItems: false
                            highlightFollowsCurrentItem: true
                            highlightMoveDuration: 280
                            highlightMoveVelocity: -1
                            highlightResizeDuration: 0
                            property bool animateRows: true
                            function syncCurrent() {
                                var s = win.selected, idx = -1
                                for (var i = 0; s && i < win.visibleItems.length; i++) {
                                    var it = win.visibleItems[i]
                                    if (it.iconKey === s.iconKey && it.username === s.username && it.name === s.name) { idx = i; break }
                                }
                                currentIndex = idx
                            }
                            onModelChanged: { animateRows = true; rowsSettle.restart(); Qt.callLater(syncCurrent) }
                            Timer { id: rowsSettle; interval: 900; onTriggered: list.animateRows = false }
                            highlight: Rectangle {
                                radius: 12
                                color: Qt.rgba(0.45, 0.65, 1, 0.30)
                                border.width: 1
                                border.color: Qt.rgba(1, 1, 1, 0.16)
                            }
                            ScrollBar.vertical: ScrollBar {
                                policy: ScrollBar.AsNeeded
                                contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Qt.rgba(1, 1, 1, 0.28) }
                            }
                            delegate: Rectangle {
                                id: rowRoot
                                required property var modelData
                                required property int index
                                readonly property string shownName: icp.displayName(modelData.iconKey, modelData.name, modelData.title || "", icp.iconRevision)
                                width: ListView.view.width - 8
                                opacity: list.animateRows ? 0 : 1
                                transform: Translate { id: rowLift; y: list.animateRows ? 10 : 0 }
                                Component.onCompleted: { if (list.animateRows) rowIn.start(); icp.requestIcon(modelData.iconKey, modelData.site || "") }
                                SequentialAnimation {
                                    id: rowIn
                                    PauseAnimation { duration: Math.min(rowRoot.index, 12) * 28 }
                                    ParallelAnimation {
                                        NumberAnimation { target: rowRoot; property: "opacity"; to: 1; duration: 320; easing.type: Easing.OutCubic }
                                        NumberAnimation { target: rowLift; property: "y"; to: 0; duration: 460; easing.type: Easing.OutExpo }
                                    }
                                }
                                height: 56
                                radius: 12
                                readonly property bool current: win.selected !== null && win.selected.iconKey === modelData.iconKey && win.selected.username === modelData.username && win.selected.name === modelData.name
                                color: !current && rowMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.07) : "transparent"
                                Behavior on color { ColorAnimation { duration: 120 } }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 12
                                    spacing: 12
                                    Monogram { label: rowRoot.shownName; source: icp.iconSource(modelData.iconKey, icp.iconRevision); size: 36 }
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2
                                        Text {
                                            text: rowRoot.shownName
                                            textFormat: Text.PlainText
                                            color: "white"; font.pixelSize: 14; font.weight: Font.DemiBold
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                        Text {
                                            text: modelData.username || icp.tr("No user name", icp.languageRevision)
                                            textFormat: Text.PlainText
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
                                    onClicked: { win.selected = modelData; list.currentIndex = rowRoot.index }
                                }
                            }

                            Text {
                                anchors.centerIn: parent
                                visible: list.count === 0
                                width: parent.width - 40
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                                textFormat: Text.PlainText
                                text: win.query ? icp.tr("No results for “{q}”", icp.languageRevision).replace("{q}", win.query) : icp.tr("Nothing here yet", icp.languageRevision)
                                color: Qt.rgba(0.86, 0.9, 1, 0.55); font.pixelSize: 13 + 1
                            }
                        }
                    }
                }

                Glass {
                    backdrop: backdrop
                    light: light
                    revealDelay: 180
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
                readonly property bool shown: !win.showSetup && (win.section === "account" || (win.vaultSection && win.needsSignIn))
                opacity: shown ? 1 : 0
                scale: shown ? 1 : 0.985
                visible: opacity > 0.01
                enabled: shown
                Behavior on opacity { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
                SignInCard {
                    anchors.centerIn: parent
                    width: Math.min(parent.width - 40, 470)
                    backdrop: backdrop
                    light: light
                    onFinished: win.section = "all"
                    onRequestSetup: win.section = "setup"
                }
            }

            // Anisette setup assistant
            Item {
                anchors.fill: parent
                readonly property bool shown: win.showSetup
                opacity: shown ? 1 : 0
                scale: shown ? 1 : 0.985
                visible: opacity > 0.01
                enabled: shown
                Behavior on opacity { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
                Flickable {
                    anchors.fill: parent
                    contentHeight: Math.max(height, setupCard.height + 40)
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    SetupCard {
                        id: setupCard
                        objectName: "setupCard"
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: Math.max(20, (parent.height - height) / 2)
                        width: Math.min(win.width - 320, 500)
                        backdrop: backdrop
                        light: light
                        onFinished: win.section = "account"
                    }
                }
            }

            // Settings + debug console
            SettingsPage {
                anchors.fill: parent
                onRequestSetup: win.section = "setup"
                light: light
                readonly property bool shown: win.section === "settings"
                opacity: shown ? 1 : 0
                scale: shown ? 1 : 0.985
                visible: opacity > 0.01
                enabled: shown
                Behavior on opacity { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
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
