import streamlit as st
import yagmail
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime
import requests
from PIL import Image as PILImage
from io import BytesIO
from reportlab.graphics.shapes import Drawing, Rect

def send_email(recipient, subject, content, attachment):
    yag = yagmail.SMTP('aunraza021@gmail.com', 'dozjccrjcqdltrbz')
    yag.send(to=recipient, subject=subject, contents=content, attachments=attachment)

def generate_salary_slip_pdf(name, salary, filename, logo_url):
    document = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Download logo
    response = requests.get(logo_url)
    img = PILImage.open(BytesIO(response.content))
    img.save("logo_temp.png")

    # Add logo and title
    logo = Image("logo_temp.png", 1.5*inch, 1*inch)
    elements.append(logo)
    elements.append(Spacer(1, 12))
    title = Paragraph("<b>Sinecure AI</b>", styles['Title'])
    elements.append(title)

    # Add date and designation
    current_date = datetime.now().strftime("%B %d, %Y")
    date_paragraph = Paragraph(f"Pay Date: {current_date}", styles['Normal'])
    designation_paragraph = Paragraph(f"Designation: Software Engineer", styles['Normal'])
    elements.append(date_paragraph)
    elements.append(designation_paragraph)
    elements.append(Spacer(1, 12))

    # Add candidate details in a table
    data = [
        ['Name', name],
        ['Gross Salary', f"${salary}"],
        ['Basic Salary', f"${salary}"],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    elements.append(table)

    # Build PDF with background border
    def on_page(canvas, doc):
        canvas.saveState()
        d = Drawing(550, 700)
        d.add(Rect(0, 0, 550, 700, strokeColor=colors.black, fillColor=None, strokeWidth=1))
        d.drawOn(canvas, 0, 0)
        canvas.restoreState()

    document.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    os.remove("logo_temp.png")  # Clean up temporary logo file

def main():
    st.set_page_config(page_title="Sinecure AI", page_icon=":moneybag:", layout="centered")

    # Add custom CSS for styling
    st.markdown("""
    <style>
        body {
            background-color: #F0F8FF;
        }
        .header {
            display: flex;
            justify-content: left;
            align-items: center;
            background-color: #4682B4;  /* Slightly more blue */
            padding: 10px;
            border-radius: 10px;
            color: white;
        }
        .header img {
            max-width: 60px;  /* Adjust logo size */
            margin-right: 20px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            margin-left: 50px;  /* Slightly right */
        }
        .container {
            max-width: 700px;
            margin: auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }
        .button {
            background-color: #87CEFA;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #4682B4;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create the header with a logo
    logo_url = "https://i.ibb.co/yXLFZVV/logo.png"

    st.markdown(f"""
    <div class="header">
        <img src="{logo_url}" alt="Logo">
        <h1>Sinecure AI</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="container">', unsafe_allow_html=True)

    st.header("Enter the details for Employees")

    candidate_names = ["Aun", "Sajjad", "Uma", "Shivani"]
    default_email = "joel@sinecure.ai"

    if 'candidates' not in st.session_state:
        st.session_state.candidates = []
    if 'current_candidate' not in st.session_state:
        st.session_state.current_candidate = 0

    current_candidate = st.session_state.current_candidate

    if current_candidate < 4:
        st.subheader(f"Employee {current_candidate + 1}")
        name = st.selectbox("Select name", candidate_names, key=f"name_{current_candidate}")
        salary = st.number_input("Enter salary", min_value=0, key=f"salary_{current_candidate}")

        if st.button("Next"):
            st.session_state.candidates.append({"name": name, "email": default_email, "salary": salary})
            st.session_state.current_candidate += 1
            st.experimental_rerun()
    else:
        st.subheader("Review and Modify Salaries")
        for i, candidate in enumerate(st.session_state.candidates):
            new_salary = st.number_input(f"Modify salary for {candidate['name']}", value=candidate['salary'], key=f"modify_salary_{i}")
            st.session_state.candidates[i]['salary'] = new_salary
        
        if st.button("Send Salary Slips"):
            for candidate in st.session_state.candidates:
                filename = f"{candidate['name']}_salary_slip.pdf"
                generate_salary_slip_pdf(candidate['name'], candidate['salary'], filename, logo_url)
                slip_content = f"Dear {candidate['name']},\n\nPlease find attached your salary slip for this month.\n\nBest regards,\nSinecure AI"
                send_email(candidate['email'], "Your Salary Slip", slip_content, filename)
                os.remove(filename)  # Remove the file after sending email to clean up
                st.success(f"Salary slip sent to {candidate['email']}")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()



