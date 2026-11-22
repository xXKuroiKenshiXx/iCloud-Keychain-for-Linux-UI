import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import QtQuick.Layouts

// First-run assistant for the anisette service: choose how, install missing tools, pick the
// iCloud for Windows files, then watch the automatic setup finish.
Item {
    id: root
    property Item backdrop
    property Item light: null
    signal finished()

    property string mode: "choose"        // choose | url
    property string folder: ""
    property string folderError: ""
    readonly property var st: icp.setup
    readonly property string step: st.phase === "running" ? "install"
                                 : st.phase === "done" ? "done"
                                 : st.phase === "error" ? "error"
                                 : mode === "url" ? "url"
                                 : mode === "choose" ? "choose"
                                 : (st.missing || []).length > 0 ? "tools" : "files"
    function tt(text) { return icp.tr(text, icp.languageRevision) }

    readonly property var installSteps: [
        { key: "copy", label: "Copying the iCloud files" },
        { key: "download", label: "Downloading Anisette-on-Wine (reviewed version)" },
        { key: "build", label: "Building the helper" },
        { key: "prepare", label: "Preparing Wine" },
        { key: "provision", label: "Registering this computer with Apple" },
        { key: "start", label: "Starting the service" }
    ]
    function stepIndex(key) {
        for (var i = 0; i < installSteps.length; i++) if (installSteps[i].key === key) return i
        return 0
    }

    implicitHeight: card.implicitHeight
    height: implicitHeight
    Behavior on height { NumberAnimation { duration: 320; easing.type: Easing.OutCubic } }
    Component.onCompleted: icp.setupRefresh()
    onStepChanged: { stepIn.restart(); if (step === "files" && !folder && (st.candidates || []).length) folder = st.candidates[0] }

    ParallelAnimation {
        id: stepIn
        NumberAnimation { target: content; property: "opacity"; from: 0; to: 1; duration: 280; easing.type: Easing.OutCubic }
        NumberAnimation { target: lift; property: "y"; from: 10; to: 0; duration: 440; easing.type: Easing.OutExpo }
    }

    FolderDialog {
        id: folderDialog
        title: root.tt("Choose the iCloud folder")
        onAccepted: {
            var path = icp.setupFolder(selectedFolder.toString())
            root.folderError = path ? "" : root.tt("That folder doesn't contain the iCloud libraries.")
            if (path) root.folder = path
        }
    }

    Glass {
        anchors.fill: parent
        backdrop: root.backdrop
        light: root.light
        revealDelay: 120
        radius: 28
        tintTop: 0.15
    }

    ColumnLayout {
        id: card
        width: parent.width
        spacing: 0

        ColumnLayout {
            id: content
            transform: Translate { id: lift }
            Layout.fillWidth: true
            Layout.margins: 34
            spacing: 14

            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 64; height: 64; radius: 18
                gradient: Gradient {
                    GradientStop { position: 0; color: root.step === "done" ? "#5fd68e" : root.step === "error" ? "#ff8a7a" : "#6db2ff" }
                    GradientStop { position: 1; color: root.step === "done" ? "#25a85c" : root.step === "error" ? "#e0414b" : "#2f6fe8" }
                }
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.35)
                Icon {
                    anchors.centerIn: parent
                    size: 32; stroke: 2; color: "white"
                    name: root.step === "done" ? "check" : root.step === "error" ? "warn"
                        : root.step === "tools" ? "terminal" : root.step === "files" ? "folder" : "sliders"
                }
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: "white"; font.pixelSize: 24; font.weight: Font.Bold
                text: root.tt(({
                    "choose": "Set up the anisette service",
                    "url": "Use your own anisette service",
                    "tools": "Install the required tools",
                    "files": "Add the iCloud for Windows files",
                    "install": "Setting up…",
                    "done": "The anisette service is running",
                    "error": "Setup didn't finish"
                })[root.step])
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
                color: Qt.rgba(0.88, 0.92, 1, 0.75); font.pixelSize: 14
                lineHeight: 1.2
                text: root.step === "error" ? (root.st.error || "") : root.tt(({
                    "choose": "Apple only accepts sign-ins from devices it recognizes. A small service on this computer creates that device identity. It never sees your Apple Account, password or passwords.",
                    "url": "Enter the address of an anisette service you run, such as anisette-rs or omnisette-server.",
                    "tools": "These programs are needed once. Run this command in a terminal; it asks for your computer password.",
                    "files": "Apple's libraries can't be downloaded here. Copy the iCloud folder from a Windows computer with iCloud for Windows 15.10.39 (Microsoft Store), then choose it.",
                    "install": "This takes a few minutes. You can leave the window open.",
                    "done": "It starts by itself every time you open the app."
                })[root.step] || "")
            }

            // ---- choose
            ColumnLayout {
                visible: root.step === "choose"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 8
                Option {
                    icon: "laptop"
                    title: root.tt("On this computer (recommended)")
                    detail: root.tt("Uses the iCloud for Windows files under Wine. Set up automatically.")
                    onPicked: { root.mode = "auto"; icp.setupRefresh() }
                }
                Option {
                    icon: "globe"
                    title: root.tt("I already have an anisette service")
                    detail: root.tt("Enter the address of a service you run yourself.")
                    onPicked: root.mode = "url"
                }
            }

            // ---- own URL
            ColumnLayout {
                visible: root.step === "url"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                Field { id: urlField; Layout.fillWidth: true; leading: "globe"; text: icp.anisetteUrl; placeholderText: "http://127.0.0.1:6969"; onAccepted: useUrl.clicked() }
                GlassButton { id: useUrl; Layout.fillWidth: true; prominent: true; text: root.tt("Use This Service"); onClicked: icp.setupUseUrl(urlField.text) }
            }

            // ---- tools
            ColumnLayout {
                visible: root.step === "tools"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                Flow {
                    Layout.fillWidth: true
                    spacing: 6
                    Repeater {
                        model: root.st.missing || []
                        delegate: Rectangle {
                            required property string modelData
                            height: 28; radius: 14
                            width: missingName.implicitWidth + 24
                            color: Qt.rgba(1, 0.75, 0.36, 0.14)
                            border.width: 1
                            border.color: Qt.rgba(1, 0.75, 0.36, 0.4)
                            Text { id: missingName; anchors.centerIn: parent; text: modelData; color: "#ffd9a0"; font.pixelSize: 12 }
                        }
                    }
                }
                Rectangle {
                    visible: (root.st.command || "") !== ""
                    Layout.fillWidth: true
                    implicitHeight: commandText.implicitHeight + 24
                    radius: 12
                    color: Qt.rgba(0, 0.01, 0.05, 0.55)
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.12)
                    Text {
                        id: commandText
                        anchors.fill: parent
                        anchors.margins: 12
                        text: root.st.command || ""
                        textFormat: Text.PlainText
                        wrapMode: Text.WrapAnywhere
                        font.family: "DejaVu Sans Mono"; font.pixelSize: 12
                        color: "#d6e4ff"
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    GlassButton { Layout.fillWidth: true; icon: "copy"; text: root.tt("Copy"); visible: (root.st.command || "") !== ""; onClicked: icp.copy(root.st.command) }
                    GlassButton { Layout.fillWidth: true; prominent: true; text: root.tt("Check Again"); onClicked: icp.setupRefresh() }
                }
            }

            // ---- iCloud files
            ColumnLayout {
                visible: root.step === "files"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                Text {
                    visible: (root.st.candidates || []).length > 0
                    text: root.tt("Found on this computer")
                    color: Qt.rgba(0.86, 0.9, 1, 0.6); font.pixelSize: 12; font.weight: Font.DemiBold
                }
                Repeater {
                    model: root.st.candidates || []
                    delegate: Rectangle {
                        id: candidate
                        required property string modelData
                        Layout.fillWidth: true
                        implicitHeight: 46
                        radius: 12
                        color: root.folder === modelData ? Qt.rgba(0.45, 0.65, 1, 0.26) : (candidateMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.10) : Qt.rgba(0, 0.02, 0.08, 0.28))
                        border.width: 1
                        border.color: root.folder === modelData ? "#78b0ff" : Qt.rgba(1, 1, 1, 0.12)
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 10
                            Icon { name: "folder"; size: 18; color: "#8ec2ff" }
                            Text { text: candidate.modelData; textFormat: Text.PlainText; color: "white"; font.pixelSize: 12; elide: Text.ElideMiddle; Layout.fillWidth: true }
                        }
                        MouseArea { id: candidateMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.folder = candidate.modelData; root.folderError = "" } }
                    }
                }
                Text {
                    visible: root.folder !== "" && (root.st.candidates || []).indexOf(root.folder) < 0
                    Layout.fillWidth: true
                    text: root.folder
                    textFormat: Text.PlainText
                    elide: Text.ElideMiddle
                    color: "#cfe3ff"; font.pixelSize: 12
                }
                Text {
                    visible: root.folderError !== ""
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: root.folderError
                    color: "#ffb0b0"; font.pixelSize: 12
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    GlassButton { Layout.fillWidth: true; icon: "folder"; text: root.tt("Choose Folder…"); onClicked: folderDialog.open() }
                    GlassButton { Layout.fillWidth: true; prominent: true; text: root.tt("Set Up Automatically"); enabled: root.folder !== ""; onClicked: icp.setupInstall(root.folder) }
                }
            }

            // ---- installing
            ColumnLayout {
                visible: root.step === "install"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 8
                Repeater {
                    model: root.installSteps
                    delegate: RowLayout {
                        id: installRow
                        required property var modelData
                        required property int index
                        readonly property int current: root.stepIndex(root.st.step || "copy")
                        Layout.fillWidth: true
                        spacing: 10
                        Rectangle {
                            width: 18; height: 18; radius: 9
                            color: installRow.index < installRow.current ? "#5fd68e" : installRow.index === installRow.current ? "#8ec2ff" : Qt.rgba(1, 1, 1, 0.16)
                            Behavior on color { ColorAnimation { duration: 240 } }
                            Icon { anchors.centerIn: parent; visible: installRow.index < installRow.current; name: "check"; size: 12; stroke: 2.2; color: "#0b1a10" }
                            SequentialAnimation on opacity {
                                running: installRow.index === installRow.current
                                loops: Animation.Infinite
                                NumberAnimation { from: 1; to: 0.35; duration: 650 }
                                NumberAnimation { from: 0.35; to: 1; duration: 650 }
                            }
                        }
                        Text {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: root.tt(installRow.modelData.label)
                            color: installRow.index <= installRow.current ? "white" : Qt.rgba(0.86, 0.9, 1, 0.5)
                            font.pixelSize: 13
                        }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.topMargin: 6
                    implicitHeight: logText.implicitHeight + 20
                    radius: 12
                    color: Qt.rgba(0, 0.01, 0.05, 0.55)
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.10)
                    Text {
                        id: logText
                        anchors.fill: parent
                        anchors.margins: 10
                        text: (root.st.log || []).join("\n") || "…"
                        textFormat: Text.PlainText
                        wrapMode: Text.WrapAnywhere
                        maximumLineCount: 6
                        elide: Text.ElideRight
                        font.family: "DejaVu Sans Mono"; font.pixelSize: 11
                        color: Qt.rgba(0.84, 0.9, 1, 0.7)
                    }
                }
            }

            GlassButton {
                visible: root.step === "error"
                Layout.fillWidth: true
                prominent: true
                text: root.tt("Try Again")
                onClicked: { icp.setupReset(); root.mode = "auto" }
            }
            GlassButton {
                visible: root.step === "done"
                Layout.fillWidth: true
                prominent: true
                text: root.tt("Continue to Sign In")
                onClicked: root.finished()
            }
            GlassButton {
                visible: root.step === "url" || root.step === "tools" || root.step === "files"
                Layout.alignment: Qt.AlignHCenter
                compact: true
                text: root.tt("Back")
                onClicked: root.mode = "choose"
            }
            Text {
                visible: (root.st.error || "") !== "" && root.step === "url"
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: root.st.error || ""
                color: "#ffb0b0"; font.pixelSize: 12
            }
        }
    }

    component Option: Rectangle {
        id: option
        property string icon
        property string title
        property string detail
        signal picked()
        Layout.fillWidth: true
        implicitHeight: optionColumn.implicitHeight + 26
        radius: 14
        color: optionMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.13) : Qt.rgba(0, 0.02, 0.08, 0.28)
        border.width: 1
        border.color: optionMouse.containsMouse ? "#78b0ff" : Qt.rgba(1, 1, 1, 0.12)
        Behavior on color { ColorAnimation { duration: 140 } }
        RowLayout {
            anchors.fill: parent
            anchors.margins: 13
            spacing: 12
            Icon { Layout.alignment: Qt.AlignTop; name: option.icon; size: 22; color: "#8ec2ff" }
            ColumnLayout {
                id: optionColumn
                Layout.fillWidth: true
                spacing: 3
                Text { Layout.fillWidth: true; text: option.title; wrapMode: Text.WordWrap; color: "white"; font.pixelSize: 14; font.weight: Font.DemiBold }
                Text { Layout.fillWidth: true; text: option.detail; wrapMode: Text.WordWrap; color: Qt.rgba(0.86, 0.9, 1, 0.65); font.pixelSize: 12 }
            }
            Icon { name: "chevron"; size: 16; color: Qt.rgba(1, 1, 1, 0.5) }
        }
        MouseArea { id: optionMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: option.picked() }
    }
}
