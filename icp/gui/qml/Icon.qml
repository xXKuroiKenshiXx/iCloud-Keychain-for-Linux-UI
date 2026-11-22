import QtQuick
import QtQuick.Shapes

// Line icons drawn on a 24-unit grid with one stroke weight.
Item {
    id: root
    property string name: "key"
    property color color: "white"
    property real size: 18
    property real stroke: 1.7
    implicitWidth: size
    implicitHeight: size

    readonly property var paths: ({
        "key": "M12 15A4 4 0 1 1 4 15A4 4 0 1 1 12 15M10.8 12.2L20 3M16.5 6.5L19 9M14.2 8.8L16.4 11",
        "grid": "M4 4H10V10H4ZM14 4H20V10H14ZM4 14H10V20H4ZM14 14H20V20H14Z",
        "clock": "M21 12A9 9 0 1 1 3 12A9 9 0 1 1 21 12M12 7V12L15.5 14",
        "wifi": "M2.5 9A14 14 0 0 1 21.5 9M5.6 12.4A9.4 9.4 0 0 1 18.4 12.4M8.8 15.8A4.8 4.8 0 0 1 15.2 15.8M12 19.3L12.01 19.3",
        "sliders": "M4 7H11M17 7H20M4 17H7M13 17H20M16 7A2.5 2.5 0 1 1 11 7A2.5 2.5 0 1 1 16 7M12 17A2.5 2.5 0 1 1 7 17A2.5 2.5 0 1 1 12 17",
        "terminal": "M3.5 5H20.5V19H3.5ZM7.5 10L10.5 12L7.5 14M12.5 15H16.5",
        "person": "M20 21A8 8 0 0 0 4 21M16 8A4 4 0 1 1 8 8A4 4 0 1 1 16 8",
        "search": "M17 11A6 6 0 1 1 5 11A6 6 0 1 1 17 11M15.5 15.5L20 20",
        "eye": "M2 12C4 8 7.5 5.5 12 5.5C16.5 5.5 20 8 22 12C20 16 16.5 18.5 12 18.5C7.5 18.5 4 16 2 12ZM15 12A3 3 0 1 1 9 12A3 3 0 1 1 15 12",
        "eyeoff": "M2 12C4 8 7.5 5.5 12 5.5C16.5 5.5 20 8 22 12C20 16 16.5 18.5 12 18.5C7.5 18.5 4 16 2 12ZM15 12A3 3 0 1 1 9 12A3 3 0 1 1 15 12M4 4L20 20",
        "copy": "M9 9H20V20H9ZM5.5 15H4V4H15V5.5",
        "sync": "M19.5 10A8 8 0 0 0 5.6 6.6L4 8.2M4 4V8.2H8.2M4.5 14A8 8 0 0 0 18.4 17.4L20 15.8M20 20V15.8H15.8",
        "globe": "M21 12A9 9 0 1 1 3 12A9 9 0 1 1 21 12M3.5 12H20.5M12 3C15 6 15 18 12 21M12 3C9 6 9 18 12 21",
        "lock": "M5.5 11H18.5V20.5H5.5ZM8 11V8A4 4 0 0 1 16 8V11",
        "chevron": "M9.5 6L15.5 12L9.5 18",
        "check": "M5 12.5L9.5 17L19 7",
        "warn": "M12 3.5L21.5 20H2.5ZM12 10V14.5M12 17.2L12.01 17.2",
        "phone": "M8 2.5H16A1.5 1.5 0 0 1 17.5 4V20A1.5 1.5 0 0 1 16 21.5H8A1.5 1.5 0 0 1 6.5 20V4A1.5 1.5 0 0 1 8 2.5ZM11 18.5H13",
        "laptop": "M5 5H19V15H5ZM2.5 18.5H21.5",
        "note": "M5 3.5H15L19 7.5V20.5H5ZM8.5 11H15.5M8.5 15H13.5",
        "folder": "M3 6.5H9.5L11.5 8.5H21V19H3Z",
        "close": "M6 6L18 18M18 6L6 18",
        "sort": "M7 4V20M7 20L3.5 16.5M7 20L10.5 16.5M17 20V4M17 4L13.5 7.5M17 4L20.5 7.5",
        "more": "M5.5 12L5.51 12M12 12L12.01 12M18.5 12L18.51 12",
        "sidebar": "M3.5 5H20.5V19H3.5ZM9.5 5V19",
        "export": "M12 15V3.5M12 3.5L8 7.5M12 3.5L16 7.5M5 12.5V20.5H19V12.5",
        "wand": "M4 20L14 10M15 3.5V6.5M19.6 5.4L17.5 7.5M21 11H18M19.6 16.1L17.5 14"
    })

    Shape {
        width: 24
        height: 24
        scale: root.size / 24
        transformOrigin: Item.TopLeft
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: root.color
            strokeWidth: root.stroke
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin
            PathSvg { path: root.paths[root.name] || root.paths["key"] }
        }
    }
}
