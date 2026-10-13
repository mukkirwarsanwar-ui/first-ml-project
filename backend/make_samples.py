from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

resumes = {
    "resume_strong.pdf": [
        "Rahul Sharma",
        "Python Developer",
        "Skills: Python, FastAPI, MySQL, scikit-learn, Docker, Git",
        "Built REST APIs with FastAPI serving machine learning models.",
        "Designed MySQL schemas and trained classification models.",
        "Deployed services using Docker on cloud platforms.",
    ],
    "resume_partial.pdf": [
        "Priya Patel",
        "Frontend Developer",
        "Skills: JavaScript, React, HTML, CSS, Node.js, SQL",
        "Built responsive web apps with React and Vite.",
        "Created Node.js backends with SQL databases.",
        "Completed an introductory course in machine learning.",
    ],
    "resume_bad.pdf": [
        "Amit Verma",
        "Head Chef",
        "Skills: Menu planning, kitchen management, food safety",
        "Managed a restaurant kitchen with a team of 12.",
        "Created seasonal menus and reduced food waste by 20 percent.",
        "Trained junior culinary staff.",
    ],
}

for filename, lines in resumes.items():
    c = canvas.Canvas(filename, pagesize=A4)
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
    c.save()
    print("Created", filename)