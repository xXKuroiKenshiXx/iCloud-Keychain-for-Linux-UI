import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

// The whole join flow in one glass card: credentials, verification code, device,
// the irreversible confirmation, the device passcode, then the result.
Item {
    id: root
    property Item backdrop
    signal finished()

    readonly property string kind: icp.prompt.kind || ""
    readonly property string step: kind !== "" ? kind
                                 : icp.stage === "working" ? "working"
                                 : (icp.stage === "done" && icp.signedIn) ? "done" : "signin"
    readonly property string deviceLine: {
        var lines = (icp.prompt.message || "").split("\n")
        for (var i = 0; i < lines.length; i++) {
            var m = lines[i].match(/passcode of:\s*(.+)$/)
            if (m) return m[1]
            m = lines[i].match(/Using the only escrow bottle:\s*(.+)$/)
            if (m) return m[1]
        }
        return ""
    }

    implicitHeight: card.implicitHeight
    height: implicitHeight

    onStepChanged: {
        answerField.text = ""
        if (step === "code" || step === "passcode" || step === "password" || step === "text" || step === "username")
            answerField.forceActiveFocus()
        if (step === "signin") email.forceActiveFocus()
    }

    Glass {
        anchors.fill: parent
        backdrop: root.backdrop
        radius: 28
        tintTop: 0.15
    }

    ColumnLayout {
        id: card
        width: parent.width
        spacing: 0

        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: 34
            spacing: 14

            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 64; height: 64; radius: 18
                gradient: Gradient {
                    GradientStop { position: 0; color: root.step === "confirm" ? "#ffb347" : root.step === "done" ? "#5fd68e" : "#6db2ff" }
                    GradientStop { position: 1; color: root.step === "confirm" ? "#e8792b" : root.step === "done" ? "#25a85c" : "#2f6fe8" }
                }
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.35)
                Icon {
                    anchors.centerIn: parent
                    size: 32; stroke: 2; color: "white"
                    name: root.step === "code" ? "phone"
                        : root.step === "device" ? "laptop"
                        : root.step === "confirm" ? "warn"
                        : root.step === "passcode" ? "lock"
                        : root.step === "done" ? "check"
                        : "key"
                }
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: "white"; font.pixelSize: 24; font.weight: Font.Bold
                text: ({
                    "signin": "Sign in with your Apple Account",
                    "working": "Connecting to iCloud",
                    "code": "Enter verification code",
                    "device": "Choose a trusted device",
                    "confirm": "Join iCloud Keychain",
                    "passcode": "Enter the device passcode",
                    "done": "iCloud Keychain is connected",
                    "password": "Enter your password",
                    "username": "Apple Account",
                    "text": "Apple needs an answer"
                })[root.step] || "Apple needs an answer"
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
                color: Qt.rgba(0.88, 0.92, 1, 0.72); font.pixelSize: 13 + 1
                lineHeight: 1.2
                text: ({
                    "signin": "This computer joins your keychain as a new device. Your password stays on this computer.",
                    "working": icp.status,
                    "code": "Apple sent a six-digit code to your trusted iPhone, iPad or Mac.",
                    "device": "Pick the device whose screen passcode you know. iCloud uses it to let this computer in.",
                    "confirm": root.deviceLine
                               ? "You'll enter the screen passcode of " + root.deviceLine + ". About ten wrong passcodes permanently erase this recovery record; one correct entry is safe."
                               : "You'll enter a device screen passcode next. About ten wrong passcodes permanently erase this recovery record; one correct entry is safe.",
                    "passcode": "The passcode you use to unlock " + (root.deviceLine || "that device") + ", not the six-digit code from Apple.",
                    "done": icp.items.length + " passwords are on this computer.",
                    "password": "Your Apple Account password.",
                    "username": "Your Apple Account email.",
                    "text": icp.prompt.message || ""
                })[root.step] || ""
            }

            // ---- credentials
            ColumnLayout {
                visible: root.step === "signin"
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 10
                Field { id: email; Layout.fillWidth: true; placeholderText: "Email or phone number"; leading: "person"; inputMethodHints: Qt.ImhEmailCharactersOnly; onAccepted: password.forceActiveFocus() }
                Field { id: password; Layout.fillWidth: true; placeholderText: "Password"; leading: "lock"; echoMode: TextInput.Password; onAccepted: signInButton.clicked() }
                GlassButton {
                    id: signInButton
                    Layout.fillWidth: true
                    Layout.topMargin: 4
                    prominent: true
                    text: "Sign In"
                    enabled: email.text.length > 3 && password.text.length > 0 && !icp.busy
                    onClicked: { icp.signIn(email.text, password.text); password.text = "" }
                }
            }

            // ---- single answer (code, passcode, generic)
            ColumnLayout {
                visible: ["code", "passcode", "password", "text", "username"].indexOf(root.step) >= 0
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 10
                Field {
                    id: answerField
                    Layout.fillWidth: true
                    implicitHeight: root.step === "code" ? 56 : 42
                    horizontalAlignment: root.step === "code" ? TextInput.AlignHCenter : TextInput.AlignLeft
                    font.pixelSize: root.step === "code" ? 26 : 14
                    font.letterSpacing: root.step === "code" ? 8 : 0
                    maximumLength: root.step === "code" ? 7 : 256
                    inputMethodHints: root.step === "code" ? Qt.ImhDigitsOnly : Qt.ImhNone
                    echoMode: (root.step === "passcode" || root.step === "password") ? TextInput.Password : TextInput.Normal
                    placeholderText: root.step === "code" ? "000000" : root.step === "passcode" ? "Device passcode" : ""
                    onAccepted: continueButton.clicked()
                }
                GlassButton {
                    id: continueButton
                    Layout.fillWidth: true
                    prominent: true
                    text: "Continue"
                    enabled: answerField.text.length > 0
                    onClicked: { icp.answer(answerField.text); answerField.text = "" }
                }
            }

            // ---- device choice
            ColumnLayout {
                visible: root.step === "device"
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 8
                Repeater {
                    model: icp.prompt.devices || []
                    delegate: Rectangle {
                        required property var modelData
                        Layout.fillWidth: true
                        implicitHeight: 54
                        radius: 14
                        color: deviceMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(0, 0.02, 0.08, 0.28)
                        border.width: 1
                        border.color: Qt.rgba(1, 1, 1, 0.12)
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 14
                            anchors.rightMargin: 14
                            spacing: 12
                            Icon { name: /mac/i.test(modelData.name) ? "laptop" : "phone"; size: 20; color: "#8ec2ff" }
                            Text { text: modelData.name; textFormat: Text.PlainText; color: "white"; font.pixelSize: 14; Layout.fillWidth: true; elide: Text.ElideRight }
                            Icon { name: "chevron"; size: 16; color: Qt.rgba(1, 1, 1, 0.5) }
                        }
                        MouseArea {
                            id: deviceMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: icp.answer(String(modelData.index))
                        }
                    }
                }
            }

            // ---- irreversible confirmation
            RowLayout {
                visible: root.step === "confirm"
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 10
                GlassButton { Layout.fillWidth: true; text: "Not Now"; onClicked: icp.confirm(false) }
                GlassButton { Layout.fillWidth: true; prominent: true; text: "I Know the Passcode"; onClicked: icp.confirm(true) }
            }

            // ---- working
            ColumnLayout {
                visible: root.step === "working"
                Layout.fillWidth: true
                Layout.topMargin: 6
                spacing: 14
                Spinner { Layout.alignment: Qt.AlignHCenter }
                GlassButton { Layout.alignment: Qt.AlignHCenter; compact: true; text: "Cancel"; onClicked: icp.cancel() }
            }

            // ---- done
            RowLayout {
                visible: root.step === "done"
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 10
                GlassButton { Layout.fillWidth: true; icon: "sync"; text: "Sync Now"; enabled: !icp.busy; onClicked: icp.sync() }
                GlassButton { Layout.fillWidth: true; prominent: true; text: "Show Passwords"; onClicked: root.finished() }
            }

            // ---- error
            Rectangle {
                visible: icp.error !== ""
                Layout.fillWidth: true
                Layout.topMargin: 4
                implicitHeight: errorText.implicitHeight + 20
                radius: 12
                color: Qt.rgba(1, 0.35, 0.35, 0.14)
                border.width: 1
                border.color: Qt.rgba(1, 0.45, 0.45, 0.35)
                Text {
                    id: errorText
                    anchors.fill: parent
                    anchors.margins: 10
                    text: icp.error
                    color: "#ffc4c4"; font.pixelSize: 12 + 1
                    wrapMode: Text.Wrap
                    textFormat: Text.PlainText
                }
            }
        }
    }

    component Spinner: Item {
        width: 34; height: 34
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: "transparent"
            border.width: 3
            border.color: Qt.rgba(1, 1, 1, 0.12)
        }
        Icon {
            id: arc
            anchors.fill: parent
            size: 34
            stroke: 2.4
            color: "#8ec2ff"
            name: "sync"
            RotationAnimation on rotation { from: 0; to: 360; duration: 1100; loops: Animation.Infinite }
        }
    }
}
