import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: win
    width: 1240
    height: 800
    minimumWidth: 980
    minimumHeight: 640
    visible: true
    title: icp.tr("Passwords", icp.languageRevision)
    color: Theme.window
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

    Backdrop { id: backdrop; anchors.fill: parent; reducedMotion: !icp.animations }

    // Pointer light shared by every glass panel; it trails the cursor for a liquid feel.
    HoverHandler { id: pointer }
    Item {
        id: light
        anchors.fill: parent
        property real px: pointer.point.position.x
        property real py: pointer.point.position.y
        readonly property bool active: pointer.hovered
        Behavior on px { enabled: icp.animations; SmoothedAnimation { velocity: 1600; duration: 260 } }
        Behavior on py { enabled: icp.animations; SmoothedAnimation { velocity: 1600; duration: 260 } }
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
            readonly property bool compact: icp.sidebarMode === "compact"
            Layout.preferredWidth: icp.sidebarMode === "full" ? 240 : compact ? 68 : 0
            Layout.fillHeight: true
            visible: Layout.preferredWidth > 1
            clip: true
            Behavior on Layout.preferredWidth { enabled: icp.animations; NumberAnimation { duration: 320; easing.type: Easing.OutCubic } }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: sidebar.compact ? 10 : 14
                spacing: 4

                RowLayout {
                    Layout.topMargin: 6
                    Layout.alignment: sidebar.compact ? Qt.AlignHCenter : Qt.AlignLeft
                    Layout.leftMargin: sidebar.compact ? 0 : 6
                    Layout.bottomMargin: 10
                    spacing: 10
                    Image {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: sidebar.compact ? 40 : 32
                        Layout.preferredHeight: sidebar.compact ? 40 : 32
                        source: Theme.dark ? "icon-dark.svg" : "icon-light.svg"
                        sourceSize.width: 64
                        sourceSize.height: 64
                        smooth: true
                    }
                    Text { visible: !sidebar.compact; text: icp.tr("Passwords", icp.languageRevision); color: Theme.text; font.pixelSize: 19; font.weight: Font.Bold }
                }

                Field {
                    id: search
                    visible: !sidebar.compact
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
                        compact: sidebar.compact
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
                    compact: sidebar.compact
                    detail: icp.busy ? "•" : ""
                    active: win.section === "account"
                    onClicked: win.section = "account"
                }
                SidebarRow {
                    Layout.fillWidth: true
                    label: icp.tr("Settings", icp.languageRevision)
                    icon: "sliders"
                    compact: sidebar.compact
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
                Behavior on opacity { enabled: icp.animations; NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { enabled: icp.animations; NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }

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
                            Layout.leftMargin: 6
                            Layout.rightMargin: 6
                            Layout.topMargin: 6
                            spacing: 6
                            ToolButton {
                                icon: "sidebar"
                                tip: icp.sidebarMode === "hidden" ? icp.tr("Show Sidebar", icp.languageRevision) : icp.tr("Hide Sidebar", icp.languageRevision)
                                onClicked: icp.toggleSidebar()
                            }
                            Item { Layout.fillWidth: true }
                            ToolButton {
                                id: sortButton
                                icon: "sort"
                                tip: icp.tr("Sort By", icp.languageRevision)
                                onClicked: sortMenu.open()
                                GlassMenu {
                                    id: sortMenu
                                    objectName: "sortMenu"
                                    y: sortButton.height + 6
                                    x: sortButton.width - width
                                    entries: {
                                        icp.languageRevision
                                        var keys = ["website", "title", "modified", "created"]
                                        var names = ["Website", "Title", "Date Edited", "Date Created"]
                                        var out = []
                                        for (var i = 0; i < keys.length; i++)
                                            out.push({ text: icp.tr(names[i], icp.languageRevision), checked: icp.sortKey === keys[i] })
                                        out.push({ separator: true })
                                        out.push({ text: icp.tr("Ascending", icp.languageRevision), checked: !icp.sortDescending })
                                        out.push({ text: icp.tr("Descending", icp.languageRevision), checked: icp.sortDescending })
                                        return out
                                    }
                                    onPicked: (index) => {
                                        var keys = ["website", "title", "modified", "created"]
                                        if (index < 4) icp.setSort(keys[index], icp.sortDescending)
                                        else if (index === 5) icp.setSort(icp.sortKey, false)
                                        else if (index === 6) icp.setSort(icp.sortKey, true)
                                    }
                                }
                            }
                            ToolButton {
                                id: moreButton
                                icon: "more"
                                tip: icp.tr("More", icp.languageRevision)
                                onClicked: moreMenu.open()
                                GlassMenu {
                                    id: moreMenu
                                    objectName: "moreMenu"
                                    y: moreButton.height + 6
                                    x: moreButton.width - width
                                    entries: [
                                        { text: icp.tr("Generate Password…", icp.languageRevision), icon: "wand" },
                                        { text: icp.tr("Export Passwords…", icp.languageRevision), icon: "export", enabled: icp.items.length > 0 }
                                    ]
                                    onPicked: (index) => {
                                        if (index === 0) generator.show()
                                        else exportWarning.open()
                                    }
                                }
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
                        Text {
                            text: win.section === "codes" ? icp.tr("Codes", icp.languageRevision) : win.section === "wifi" ? icp.tr("Wi-Fi", icp.languageRevision) : icp.tr("All Passwords", icp.languageRevision)
                            color: Theme.text; font.pixelSize: 22; font.weight: Font.Bold
                            Layout.fillWidth: true
                            Layout.leftMargin: 10
                            Layout.rightMargin: 10
                            Layout.topMargin: -6
                            Layout.minimumWidth: 0
                            elide: Text.ElideRight
                            fontSizeMode: Text.HorizontalFit
                            minimumPixelSize: 16
                        }

                        Field {
                            visible: icp.sidebarMode !== "full"
                            Layout.fillWidth: true
                            Layout.leftMargin: 6
                            Layout.rightMargin: 6
                            implicitHeight: 36
                            leading: "search"
                            placeholderText: icp.tr("Search", icp.languageRevision)
                            text: search.text
                            onTextChanged: if (search.text !== text) search.text = text
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
                            highlightMoveDuration: icp.animations ? 280 : 0
                            highlightMoveVelocity: -1
                            highlightResizeDuration: 0
                            property bool animateRows: false
                            function syncCurrent() {
                                var s = win.selected, idx = -1
                                for (var i = 0; s && i < win.visibleItems.length; i++) {
                                    var it = win.visibleItems[i]
                                    if (it.iconKey === s.iconKey && it.username === s.username && it.name === s.name) { idx = i; break }
                                }
                                currentIndex = idx
                            }
                            // Rows glide in only when the list first fills, not on every re-sort or sync.
                            property bool filledOnce: false
                            onModelChanged: { if (!filledOnce && win.visibleItems.length > 0) { filledOnce = true; animateRows = true; rowsSettle.restart() } Qt.callLater(syncCurrent) }
                            Timer { id: rowsSettle; interval: 900; onTriggered: list.animateRows = false }
                            highlight: Rectangle {
                                radius: 12
                                color: Theme.selection
                                border.width: 1
                                border.color: Theme.overlay(0.16)
                            }
                            ScrollBar.vertical: ScrollBar {
                                policy: ScrollBar.AsNeeded
                                contentItem: Rectangle { implicitWidth: 5; radius: 3; color: Theme.overlay(0.28) }
                            }
                            delegate: Rectangle {
                                id: rowRoot
                                required property var modelData
                                required property int index
                                readonly property string shownName: icp.displayName(modelData.iconKey, modelData.name, modelData.title || "", icp.iconRevision)
                                width: ListView.view.width - 8
                                readonly property bool entering: list.animateRows && icp.animations
                                opacity: entering ? 0 : 1
                                transform: Translate { id: rowLift; y: rowRoot.entering ? 10 : 0 }
                                Component.onCompleted: { if (entering) rowIn.start(); icp.requestIcon(modelData.iconKey, modelData.site || "") }
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
                                color: !current && rowMouse.containsMouse ? Theme.overlay(0.07) : "transparent"
                                Behavior on color { enabled: icp.animations; ColorAnimation { duration: 120 } }
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
                                            color: Theme.text; font.pixelSize: 14; font.weight: Font.DemiBold
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                        Text {
                                            text: modelData.username || icp.tr("No user name", icp.languageRevision)
                                            textFormat: Text.PlainText
                                            color: Theme.secondary(0.62); font.pixelSize: 12 + 1
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                    }
                                    Icon { visible: !!modelData.totp; name: "clock"; size: 14; color: Theme.secondary(0.6) }
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
                                color: Theme.secondary(0.55); font.pixelSize: 13 + 1
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
                Behavior on opacity { enabled: icp.animations; NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { enabled: icp.animations; NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
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
                Behavior on opacity { enabled: icp.animations; NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { enabled: icp.animations; NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
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
                Behavior on opacity { enabled: icp.animations; NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on scale { enabled: icp.animations; NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
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
            Text { text: toast.message; color: Theme.text; font.pixelSize: 13; anchors.verticalCenter: parent.verticalCenter }
        }
    }
    // ---------------------------------------------------------------- password generator
    Popup {
        id: generator
        objectName: "generator"
        parent: Overlay.overlay
        property string value: ""
        function show() { value = icp.generatePassword(); open() }
        anchors.centerIn: parent
        width: 420
        padding: 24
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        Overlay.modal: Rectangle { color: Qt.rgba(0, 0, 0, 0.35) }
        enter: Transition { enabled: icp.animations; NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180 } }
        background: Rectangle { radius: 22; color: Theme.popup; border.width: 1; border.color: Theme.overlay(0.18) }
        contentItem: ColumnLayout {
            spacing: 14
            RowLayout {
                spacing: 10
                Icon { name: "wand"; size: 20; color: Theme.accent }
                Text { text: icp.tr("Strong Password", icp.languageRevision); color: Theme.text; font.pixelSize: 18; font.weight: Font.Bold }
            }
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 58
                radius: 14
                color: Theme.inset(0.55)
                border.width: 1
                border.color: Theme.overlay(0.12)
                Text {
                    anchors.centerIn: parent
                    text: generator.value
                    font.family: "DejaVu Sans Mono"; font.pixelSize: 19; font.letterSpacing: 0.5
                    color: Theme.text
                }
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                GlassButton { Layout.fillWidth: true; icon: "sync"; text: icp.tr("Generate Another", icp.languageRevision); onClicked: generator.value = icp.generatePassword() }
                GlassButton { Layout.fillWidth: true; prominent: true; icon: "copy"; text: icp.tr("Copy", icp.languageRevision); onClicked: { icp.copy(generator.value); generator.close() } }
            }
        }
    }

    // ---------------------------------------------------------------- export
    Popup {
        id: exportWarning
        objectName: "exportWarning"
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: 440
        padding: 24
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        Overlay.modal: Rectangle { color: Qt.rgba(0, 0, 0, 0.35) }
        enter: Transition { enabled: icp.animations; NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180 } }
        background: Rectangle { radius: 22; color: Theme.popup; border.width: 1; border.color: Qt.rgba(1, 0.75, 0.36, 0.4) }
        contentItem: ColumnLayout {
            spacing: 14
            RowLayout {
                spacing: 10
                Icon { name: "warn"; size: 20; color: "#ffbe5c" }
                Text { text: icp.tr("Export Passwords…", icp.languageRevision); color: Theme.text; font.pixelSize: 18; font.weight: Font.Bold }
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: icp.tr("Exported passwords aren't encrypted. Anyone who gets the file can read every password in it. Delete it when you're done.", icp.languageRevision)
                color: Theme.warningText; font.pixelSize: 13; lineHeight: 1.2
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                GlassButton { Layout.fillWidth: true; text: icp.tr("Cancel", icp.languageRevision); onClicked: exportWarning.close() }
                GlassButton { Layout.fillWidth: true; prominent: true; icon: "export"; text: icp.tr("Export…", icp.languageRevision); onClicked: { exportWarning.close(); exportDialog.open() } }
            }
        }
    }
    FileDialog {
        id: exportDialog
        fileMode: FileDialog.SaveFile
        defaultSuffix: "csv"
        selectedFile: "file:///" + "Passwords.csv"
        nameFilters: ["CSV (*.csv)"]
        onAccepted: icp.exportCsv(selectedFile.toString())
    }

    component ToolButton: GlassButton {
        property string tip: ""
        compact: true
        implicitWidth: implicitHeight
        ToolTip.visible: tipHover.hovered && tip !== ""
        ToolTip.delay: 400
        ToolTip.text: tip
        HoverHandler { id: tipHover }
    }
}
