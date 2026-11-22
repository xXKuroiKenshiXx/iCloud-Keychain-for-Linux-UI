import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

// The whole join flow in one glass card: credentials, verification code, device,
// the irreversible confirmation, the device passcode, then the result.
Item {
    id: root
    property Item backdrop
    property Item light: null
    signal finished()

    readonly property string kind: icp.prompt.kind || ""
    readonly property string step: kind !== "" ? kind
                                 : icp.stage === "working" ? "working"
                                 : (icp.stage === "done" && icp.signedIn) ? "done" : "signin"
    property string lastDevice: ""
    readonly property string deviceLine: {
        var lines = (icp.prompt.message || "").split("\n")
        for (var i = 0; i < lines.length; i++) {
            var m = lines[i].match(/passcode of:\s*(.+)$/)
            if (m) return m[1]
            m = lines[i].match(/Using the only escrow bottle:\s*(.+)$/)
            if (m) return m[1]
        }
        return root.lastDevice
    }
    onDeviceLineChanged: if (deviceLine) lastDevice = deviceLine

    // Progress through the four things Apple asks for.
    readonly property int stage: ({ "signin": 0, "working": 0, "password": 0, "username": 0, "text": 0,
                                    "code": 1, "device": 2, "confirm": 3, "passcode": 3, "done": 4 })[step] || 0
    readonly property var stageNames: ["Account", "Code", "Device", "Passcode"]
    readonly property bool canCancel: ["code", "device", "passcode", "text", "working"].indexOf(step) >= 0

    implicitHeight: card.implicitHeight
    height: implicitHeight
    Behavior on height { NumberAnimation { duration: 320; easing.type: Easing.OutCubic } }

    ParallelAnimation {
        id: stepIn
        NumberAnimation { target: stepContent; property: "opacity"; from: 0; to: 1; duration: 280; easing.type: Easing.OutCubic }
        NumberAnimation { target: stepLift; property: "y"; from: 10; to: 0; duration: 440; easing.type: Easing.OutExpo }
    }

    onStepChanged: {
        stepIn.restart()
        answerField.text = ""
        if (step === "code" || step === "passcode" || step === "password" || step === "text" || step === "username")
            answerField.forceActiveFocus()
        if (step === "signin") email.forceActiveFocus()
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
            id: stepContent
            transform: Translate { id: stepLift }
            Layout.fillWidth: true
            Layout.margins: 34
            spacing: 14

            Row {
                Layout.alignment: Qt.AlignHCenter
                Layout.bottomMargin: 6
                spacing: 6
                visible: root.step !== "done"
                Repeater {
                    model: root.stageNames
                    delegate: Row {
                        id: dot
                        required property string modelData
                        required property int index
                        spacing: 6
                        height: 16
                        Rectangle {
                            width: dot.index === root.stage ? 22 : 8
                            height: 8
                            radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: dot.index < root.stage ? "#5fd68e" : dot.index === root.stage ? "#8ec2ff" : Qt.rgba(1, 1, 1, 0.22)
                            Behavior on width { NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
                            Behavior on color { ColorAnimation { duration: 260 } }
                        }
                        Text {
                            visible: dot.index === root.stage
                            text: icp.tr(dot.modelData, icp.languageRevision)
                            color: "#cfe3ff"; font.pixelSize: 12; font.weight: Font.DemiBold
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }

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
                    "signin": icp.tr("Sign in with your Apple Account", icp.languageRevision),
                    "working": icp.tr("Connecting to iCloud", icp.languageRevision),
                    "code": icp.tr("Enter the verification code", icp.languageRevision),
                    "device": icp.tr("Choose a trusted device", icp.languageRevision),
                    "confirm": icp.tr("Join iCloud Keychain", icp.languageRevision),
                    "passcode": icp.tr("Enter the device passcode", icp.languageRevision),
                    "done": icp.tr("iCloud Keychain is connected", icp.languageRevision),
                    "password": icp.tr("Enter your password", icp.languageRevision),
                    "username": icp.tr("Apple Account", icp.languageRevision),
                    "text": icp.tr("Apple needs an answer", icp.languageRevision)
                })[root.step] || icp.tr("Apple needs an answer", icp.languageRevision)
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
                color: Qt.rgba(0.88, 0.92, 1, 0.75); font.pixelSize: 14
                lineHeight: 1.2
                text: ({
                    "signin": icp.tr("This computer joins your iCloud Keychain as a new device. Your password is sent only to Apple and is never shown or logged.", icp.languageRevision),
                    "working": icp.status,
                    "code": icp.tr("Apple just showed a six-digit code on your iPhone, iPad or Mac. If it first asks to Allow a sign-in, tap Allow.", icp.languageRevision),
                    "device": icp.tr("Pick the device whose screen passcode you know. Its passcode is what lets this computer read your passwords.", icp.languageRevision),
                    "confirm": icp.tr("Next you'll type the screen passcode of {device}.", icp.languageRevision).replace("{device}", root.deviceLine || icp.tr("that device", icp.languageRevision)),
                    "passcode": icp.tr("The passcode you use to unlock {device}, not your Apple Account password and not the six-digit code.", icp.languageRevision).replace("{device}", root.deviceLine || icp.tr("that device", icp.languageRevision)),
                    "done": icp.tr("{n} passwords are now on this computer, encrypted.", icp.languageRevision).replace("{n}", icp.items.length),
                    "password": icp.tr("Your Apple Account password.", icp.languageRevision),
                    "username": icp.tr("Your Apple Account email.", icp.languageRevision),
                    "text": icp.prompt.message || ""
                })[root.step] || ""
            }

            Notice {
                visible: root.step === "signin" && icp.anisetteState === 0
                tone: "error"
                text: icp.tr("The anisette service at {url} isn't answering. Sign-in needs it: start it, then press Check Again.", icp.languageRevision).replace("{url}", icp.anisetteUrl)
                action: icp.tr("Check Again", icp.languageRevision)
                onActivated: icp.checkAnisette()
            }
            Notice {
                visible: root.step === "code"
                tone: "info"
                text: icp.tr("No code? Unlock one of your Apple devices and wait a minute with this window open. Asking for codes repeatedly can block sign-in for a while.", icp.languageRevision)
            }
            Notice {
                visible: root.step === "confirm" || root.step === "passcode"
                tone: "warning"
                text: icp.tr("Each wrong passcode uses one of about ten recovery attempts. After the last one Apple permanently erases this recovery record. One correct entry is safe.", icp.languageRevision)
            }

            // ---- credentials
            ColumnLayout {
                visible: root.step === "signin"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                Field {
                    id: email
                    Layout.fillWidth: true
                    placeholderText: icp.tr("Apple Account email or phone", icp.languageRevision)
                    leading: "person"
                    inputMethodHints: Qt.ImhEmailCharactersOnly | Qt.ImhNoAutoUppercase
                    onAccepted: password.forceActiveFocus()
                }
                Field {
                    id: password
                    Layout.fillWidth: true
                    placeholderText: icp.tr("Password", icp.languageRevision)
                    leading: "lock"
                    secret: true
                    onAccepted: if (signInButton.enabled) signInButton.clicked()
                }
                GlassButton {
                    id: signInButton
                    Layout.fillWidth: true
                    Layout.topMargin: 4
                    prominent: true
                    text: icp.tr("Sign In", icp.languageRevision)
                    enabled: email.text.trim().length > 3 && password.text.length > 0 && !icp.busy
                    onClicked: { icp.signIn(email.text, password.text); password.text = ""; password.shown = false }
                }
            }

            // ---- single answer (code, passcode, generic)
            ColumnLayout {
                visible: ["code", "passcode", "password", "text", "username"].indexOf(root.step) >= 0
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                Field {
                    id: answerField
                    Layout.fillWidth: true
                    implicitHeight: root.step === "code" ? 58 : 44
                    horizontalAlignment: root.step === "code" ? TextInput.AlignHCenter : TextInput.AlignLeft
                    font.pixelSize: root.step === "code" ? 26 : 15
                    font.letterSpacing: root.step === "code" ? 8 : 0
                    maximumLength: root.step === "code" ? 7 : 256
                    validator: root.step === "code" ? digits : null
                    secret: root.step === "passcode" || root.step === "password"
                    leading: root.step === "passcode" ? "lock" : ""
                    placeholderText: root.step === "code" ? "000 000" : root.step === "passcode" ? icp.tr("Device passcode", icp.languageRevision) : ""
                    onAccepted: if (continueButton.enabled) continueButton.clicked()
                    RegularExpressionValidator { id: digits; regularExpression: /[0-9 ]{0,7}/ }
                }
                GlassButton {
                    id: continueButton
                    Layout.fillWidth: true
                    prominent: true
                    text: root.step === "passcode" ? icp.tr("Join Keychain", icp.languageRevision) : icp.tr("Continue", icp.languageRevision)
                    enabled: root.step === "code" ? answerField.text.replace(/\D/g, "").length === 6 : answerField.text.length > 0
                    onClicked: { icp.answer(answerField.text); answerField.text = ""; answerField.shown = false }
                }
            }

            // ---- device choice
            ColumnLayout {
                visible: root.step === "device"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 8
                Repeater {
                    model: icp.prompt.devices || []
                    delegate: Rectangle {
                        id: deviceRow
                        required property var modelData
                        Layout.fillWidth: true
                        implicitHeight: 56
                        radius: 14
                        color: deviceMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(0, 0.02, 0.08, 0.28)
                        border.width: 1
                        border.color: deviceMouse.containsMouse ? "#78b0ff" : Qt.rgba(1, 1, 1, 0.12)
                        Behavior on color { ColorAnimation { duration: 140 } }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 14
                            anchors.rightMargin: 14
                            spacing: 12
                            Icon { name: /mac/i.test(deviceRow.modelData.name) ? "laptop" : "phone"; size: 20; color: "#8ec2ff" }
                            Text { text: deviceRow.modelData.name; textFormat: Text.PlainText; color: "white"; font.pixelSize: 14; Layout.fillWidth: true; elide: Text.ElideRight }
                            Icon { name: "chevron"; size: 16; color: Qt.rgba(1, 1, 1, 0.5) }
                        }
                        MouseArea {
                            id: deviceMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: { root.lastDevice = deviceRow.modelData.name; icp.answer(String(deviceRow.modelData.index)) }
                        }
                    }
                }
            }

            // ---- irreversible confirmation
            RowLayout {
                visible: root.step === "confirm"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                GlassButton { Layout.fillWidth: true; text: icp.tr("Not Now", icp.languageRevision); onClicked: icp.confirm(false) }
                GlassButton { Layout.fillWidth: true; prominent: true; text: icp.tr("I Know the Passcode", icp.languageRevision); onClicked: icp.confirm(true) }
            }

            Spinner {
                visible: root.step === "working"
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 4
            }

            // ---- done
            RowLayout {
                visible: root.step === "done"
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10
                GlassButton { Layout.fillWidth: true; icon: "sync"; text: icp.tr("Sync Now", icp.languageRevision); enabled: !icp.busy; onClicked: icp.sync() }
                GlassButton { Layout.fillWidth: true; prominent: true; text: icp.tr("Show Passwords", icp.languageRevision); onClicked: root.finished() }
            }

            GlassButton {
                visible: root.canCancel
                Layout.alignment: Qt.AlignHCenter
                compact: true
                text: icp.tr("Cancel Sign-In", icp.languageRevision)
                onClicked: icp.cancel()
            }

            Notice {
                visible: icp.error !== ""
                tone: "error"
                text: icp.error
            }
        }
    }

    component Notice: Rectangle {
        id: notice
        property string tone: "info"          // info | warning | error
        property string text: ""
        property string action: ""
        signal activated()
        readonly property color hue: tone === "error" ? "#ff7a7a" : tone === "warning" ? "#ffbe5c" : "#7db7ff"
        Layout.fillWidth: true
        implicitHeight: noticeRow.implicitHeight + 22
        radius: 12
        color: Qt.alpha(hue, 0.13)
        border.width: 1
        border.color: Qt.alpha(hue, 0.38)
        RowLayout {
            id: noticeRow
            anchors.fill: parent
            anchors.margins: 11
            spacing: 10
            Icon {
                Layout.alignment: Qt.AlignTop
                name: notice.tone === "info" ? "check" : "warn"
                size: 16
                color: notice.hue
            }
            Text {
                Layout.fillWidth: true
                text: notice.text
                textFormat: Text.PlainText
                wrapMode: Text.WordWrap
                color: Qt.lighter(notice.hue, 1.45)
                font.pixelSize: 13
                lineHeight: 1.15
            }
            GlassButton {
                visible: notice.action !== ""
                compact: true
                text: notice.action
                onClicked: notice.activated()
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
            anchors.fill: parent
            size: 34
            stroke: 2.4
            color: "#8ec2ff"
            name: "sync"
            RotationAnimation on rotation { from: 0; to: 360; duration: 1100; loops: Animation.Infinite }
        }
    }
}
