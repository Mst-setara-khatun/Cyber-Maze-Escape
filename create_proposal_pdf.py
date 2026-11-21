from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, KeepTogether
)
from reportlab.platypus import Image as RLImage
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from pathlib import Path
import os

desktop = Path.home() / "Desktop"
if not desktop.exists():
    desktop = Path(os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop"))
    if not desktop.exists():
        desktop = Path.home()

output = desktop / "Cyber-Maze-Escape-Project-Proposal-Final.pdf"

DARK = HexColor("#10251F")
GREEN = HexColor("#176B50")
GOLD = HexColor("#C69B45")
LIGHT = HexColor("#EDF4EF")
TEXT = HexColor("#26332D")
MUTED = HexColor("#65736B")

doc = SimpleDocTemplate(
    str(output),
    pagesize=A4,
    rightMargin=18*mm,
    leftMargin=18*mm,
    topMargin=20*mm,
    bottomMargin=18*mm,
    title="Cyber Maze Escape - Project Proposal",
    author="MST. SETARA KHATUN",
    subject="Computer Graphics and Multimedia System"
)

styles = getSampleStyleSheet()

cover_title = ParagraphStyle(
    "CoverTitle", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=29,
    leading=36, alignment=TA_CENTER,
    textColor=DARK, spaceAfter=12
)

cover_sub = ParagraphStyle(
    "CoverSub", parent=styles["Normal"],
    fontName="Helvetica", fontSize=16,
    leading=23, alignment=TA_CENTER,
    textColor=GREEN
)

heading = ParagraphStyle(
    "SectionHeading", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=12,
    leading=16, textColor=GREEN,
    spaceBefore=9, spaceAfter=5,
    keepWithNext=True
)

body = ParagraphStyle(
    "BodyTextCustom", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=9.1,
    leading=13.2, textColor=TEXT,
    alignment=TA_JUSTIFY, spaceAfter=5
)

bullet = ParagraphStyle(
    "BulletCustom", parent=body,
    leftIndent=12, firstLineIndent=-8,
    spaceAfter=2
)

small = ParagraphStyle(
    "SmallCustom", parent=body,
    fontSize=8, leading=10.5
)

center = ParagraphStyle(
    "CenterCustom", parent=body,
    alignment=TA_CENTER
)

story = []

def P(text, style=body):
    return Paragraph(text, style)

def section(number, title, content):
    story.append(P(f"{number}. {title}", heading))
    if isinstance(content, str):
        story.append(P(content))
    else:
        story.extend(content)

def bullets(items):
    return [
        P("&bull; " + item, bullet)
        for item in items
    ]

def make_table(data, widths, header=True):
    converted = []
    for row_index, row in enumerate(data):
        converted.append([
            P(str(cell), ParagraphStyle(
                f"table_{row_index}_{i}",
                parent=small,
                fontName="Helvetica-Bold" if row_index == 0 and header else "Helvetica",
                textColor=colors.white if row_index == 0 and header else TEXT
            ))
            for i, cell in enumerate(row)
        ])

    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0,0), (-1,-1), 0.4, HexColor("#CBD7CE")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0,0), (-1,0), GREEN),
        ]
        for row in range(1, len(data)):
            if row % 2 == 0:
                commands.append(("BACKGROUND", (0,row), (-1,row), LIGHT))
    t.setStyle(TableStyle(commands))
    return t



# FINAL UNIVERSITY COVER PAGE

logo_path = Path("Assets/University/nubtk_logo.png")

if not logo_path.exists():
    raise FileNotFoundError("University logo not found!")

university_logo = RLImage(
    str(logo_path),
    width=68*mm,
    height=45*mm,
    kind="proportional"
)
university_logo.hAlign = "CENTER"

story.append(Spacer(1, 2*mm))
story.append(university_logo)
story.append(Spacer(1, 5*mm))

story.append(P(
    "PROJECT PROPOSAL",
    ParagraphStyle(
        "TopLabelFinal",
        parent=cover_sub,
        fontSize=12,
        leading=18,
        textColor=GOLD
    )
))

story.append(Spacer(1, 5*mm))
story.append(P("CYBER MAZE<br/>ESCAPE", cover_title))
story.append(P("A 3D Maze Adventure Game", cover_sub))
story.append(Spacer(1, 8*mm))

cover_data = [
    ["ACADEMIC INFORMATION", "DETAILS"],
    ["Student Name", "MST. SETARA KHATUN"],
    ["Student ID", "11230321387"],
    ["Submitted To", "Uma Datta"],
    ["Course Title", "Computer Graphics and Multimedia System Lab"],
    ["Course Code", "CSE 4108"],
    ["Project Type", "Individual Game Development Project"],
    ["Technology", "Python and Pygame-CE"],
    ["Project Duration", "6 Weeks"],
]

story.append(make_table(cover_data, [43*mm, 105*mm]))
story.append(Spacer(1, 8*mm))

story.append(P(
    "EXPLORE  |  SURVIVE  |  ESCAPE",
    ParagraphStyle(
        "TaglineFinal",
        parent=cover_sub,
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=GOLD
    )
))

story.append(Spacer(1, 8*mm))

story.append(P(
    "Submitted By<br/><b>MST. SETARA KHATUN</b><br/>"
    "Student ID: 11230321387",
    center
))

story.append(Spacer(1, 9*mm))

signature_data = [
    ["____________________________", "____________________________"],
    ["Teacher's Signature", "Date"],
]

signature_table = Table(
    signature_data,
    colWidths=[74*mm, 74*mm],
    rowHeights=[9*mm, 6*mm]
)

signature_table.setStyle(TableStyle([
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("TEXTCOLOR", (0,0), (-1,-1), DARK),
]))

story.append(signature_table)
story.append(PageBreak())

# PAGE 2 CONTENT
story.append(P("PROJECT OVERVIEW", heading))

section("1", "Introduction",
    "Cyber Maze Escape is a futuristic 3D-style maze adventure game developed "
    "using Python and Pygame-CE. The game places players inside a mysterious "
    "futuristic cyber environment where they must explore complex mazes, "
    "overcome obstacles, collect keys, unlock doors and find the final escape "
    "route. The project focuses on computer graphics concepts, interactive "
    "gameplay, player movement, collision detection and visual effects."
)

section("2", "Project Background and Motivation",
    "Maze games are an interesting way to demonstrate navigation, spatial "
    "awareness and interactive computer graphics. The motivation behind this "
    "project is to develop an engaging futuristic maze adventure game that "
    "demonstrates practical applications of computer graphics concepts through "
    "an interactive gaming experience."
)

section("3", "Problem Statement",
    "Players need to navigate through a challenging maze environment while "
    "avoiding obstacles and finding the correct escape route. The game will "
    "provide an interactive environment where players must use navigation "
    "skills, solve challenges and complete objectives within the game."
)

section("4", "Project Objectives", bullets([
    "Develop a visually attractive futuristic maze adventure game.",
    "Implement a first-person 3D-style maze environment.",
    "Provide smooth player movement and collision detection.",
    "Implement interactive keys and locked doors.",
    "Add scoring, timer and game status information.",
    "Develop a complete game experience with winning and losing conditions."
]))

section("5", "Game Concept and Story",
    "The player enters a mysterious cyber facility that has been locked by an "
    "unknown security system. To escape, the player must explore the maze, "
    "discover hidden keys, unlock restricted doors and reach the final exit. "
    "Each challenge is designed to make the adventure more interesting and engaging."
)

section("6", "Gameplay Description",
    "The game starts with a futuristic main menu. After selecting Start Game, "
    "the player enters a first-person 3D-style maze environment. The player "
    "explores the maze using keyboard controls, collects required keys and "
    "unlocks doors. The player must reach the final exit before the timer runs "
    "out. Successful completion displays a winning screen, while failure "
    "displays a game-over screen."
)

# PAGE 3 FEATURES
story.append(P("GAME FEATURES AND DESIGN", heading))

section("7", "Main Features", [
    P("<b>Feature 1: Futuristic Main Menu</b>", body),
    *bullets([
        "Professional cyberpunk-style interface.",
        "Animated background and neon visual effects.",
        "Start Game and Exit Game buttons.",
        "Consistent futuristic design."
    ]),
    P("<b>Feature 2: 3D Maze Environment</b>", body),
    *bullets([
        "First-person 3D-style maze rendering using ray casting.",
        "Futuristic wall and floor design.",
        "Neon lighting and visual effects.",
        "Maze navigation environment."
    ]),
    P("<b>Feature 3: Player Movement</b>", body),
    *bullets([
        "Keyboard-based player movement.",
        "Forward, backward and sideways movement.",
        "Camera rotation.",
        "Wall collision detection to prevent passing through walls."
    ]),
    P("<b>Feature 4: Key and Door System</b>", body),
    *bullets([
        "Collectible keys placed inside the maze.",
        "Locked doors that require keys.",
        "Interactive door unlocking.",
        "Access to restricted maze areas."
    ]),
    P("<b>Feature 5: Game HUD and Scoring</b>", body),
    *bullets([
        "Player score display.",
        "Countdown timer.",
        "Current level information.",
        "Key collection status and game progress information."
    ]),
    P("<b>Feature 6: Game Completion System</b>", body),
    *bullets([
        "Winning screen after reaching the exit.",
        "Game-over screen when the player fails.",
        "Restart and return-to-menu options.",
        "Background music and sound effects."
    ])
])

section("8", "Game Rules and Objectives", bullets([
    "The player must explore the maze.",
    "The player must find the required keys.",
    "Locked doors must be opened using keys.",
    "The player must avoid obstacles.",
    "The player must reach the final exit before time expires.",
    "Completing the maze successfully results in victory."
]))

section("9", "Game Controls", [
    make_table([
        ["Key", "Action"],
        ["W", "Move Forward"],
        ["S", "Move Backward"],
        ["A", "Move Left"],
        ["D", "Move Right"],
        ["Mouse", "Camera Control (planned)"],
        ["ESC", "Pause or Return to Menu"]
    ], [45*mm, 103*mm])
])

# PAGE 4 TECHNICAL PLAN
story.append(P("TECHNICAL PLAN AND OUTCOMES", heading))

section("10", "Graphics and Visual Design",
    "The game will follow a futuristic cyberpunk visual style. The design will "
    "include dark navy and black backgrounds, neon cyan, electric blue and "
    "purple lighting, glowing interface elements, animated particles and "
    "visual effects, and first-person 3D-style maze rendering. All game screens "
    "will maintain a consistent visual design."
)

section("11", "Technologies and Tools", [
    make_table([
        ["Category", "Technology"],
        ["Programming Language", "Python"],
        ["Game Development Library", "Pygame-CE"],
        ["Graphics Technique", "Ray Casting"],
        ["Development Environment", "Visual Studio Code"],
        ["Version Control", "Git and GitHub"]
    ], [55*mm, 93*mm])
])

section("12", "Six-Week Development Timeline", [
    make_table([
        ["Week", "Feature", "Planned Work"],
        ["1", "Futuristic Main Menu", "Project setup and interactive main menu"],
        ["2", "3D Maze Environment", "Maze design and ray-casting renderer"],
        ["3", "Player Movement", "Movement, camera and collision detection"],
        ["4", "Key and Door System", "Key collection and door unlocking"],
        ["5", "Game HUD and Scoring", "Timer, score and game information"],
        ["6", "Game Completion System", "Win/lose screens, restart and sound effects"]
    ], [17*mm, 43*mm, 88*mm])
])

section("13", "Expected Outcomes",
    "The expected outcome is a complete and interactive futuristic 3D-style "
    "maze adventure game. The final game will demonstrate practical computer "
    "graphics concepts, interactive controls, maze navigation, collision "
    "detection and game development techniques."
)

section("14", "Conclusion",
    "Cyber Maze Escape aims to combine computer graphics concepts with an "
    "engaging futuristic gaming experience. Through six weeks of development, "
    "the project will gradually introduce six major features and deliver a "
    "visually consistent and interactive maze adventure game."
)

story.append(Spacer(1, 9))
story.append(Table(
    [[P("<b>PROJECT:</b> Cyber Maze Escape",
       small),
      P("<b>DEVELOPER:</b> MST. SETARA KHATUN", small),
      P("<b>DURATION:</b> 6 Weeks", small)]],
    colWidths=[48*mm, 65*mm, 35*mm],
    style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("BOX", (0,0), (-1,-1), 0.7, GREEN),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ])
))

def page_decor(canvas, doc):
    canvas.saveState()
    w, h = A4

    if doc.page > 1:
        canvas.setStrokeColor(GREEN)
        canvas.setLineWidth(0.7)
        canvas.line(18*mm, h-13*mm, w-18*mm, h-13*mm)

        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(GREEN)
        canvas.drawString(18*mm, h-10*mm, "CYBER MAZE ESCAPE")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(
            w-18*mm, h-10*mm, "PROJECT PROPOSAL"
        )

        canvas.setStrokeColor(HexColor("#CBD7CE"))
        canvas.line(18*mm, 13*mm, w-18*mm, 13*mm)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            18*mm, 8*mm, "MST. SETARA KHATUN"
        )
        canvas.drawRightString(
            w-18*mm, 8*mm, f"Page {doc.page}"
        )

    canvas.restoreState()

doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)

print("\nPDF CREATED SUCCESSFULLY!")
print("File:", output)
print("Size:", round(output.stat().st_size / 1024, 1), "KB")
print("Location: Desktop")
