from flask import Flask, render_template, request, redirect, url_for
import psycopg2
app = Flask(__name__)


# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="ayaan",
        port="5432"
    )
from flask import request, redirect, url_for

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        email = request.form["email"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO patients
            (name, age, gender, phone, address, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, gender, phone, address, email))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("view_patients"))

    return render_template("add_patient.html")

def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        email = request.form["email"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO patients
            (name, age, gender, phone, address, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, gender, phone, address, email))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("view_patients"))

    return render_template("add_patient.html")
@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patients")
    patients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM doctors")
    doctors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    appointments = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        patients=patients,
        doctors=doctors,
        appointments=appointments
    )
@app.route("/patients")
def view_patients():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT patient_id, name, age, gender, phone, address, email
        FROM patients
        ORDER BY patient_id
    """)

    patients = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("patients.html", patients=patients)

@app.route("/search_patient")
def search_patient():
    name = request.args.get("name", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT patient_id, name, age, gender, phone, address, email
        FROM patients
        WHERE name ILIKE %s
        ORDER BY patient_id
    """, ('%' + name + '%',))

    patients = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "patients.html",
        patients=patients,
        search_name=name
    )
@app.route("/update_patient/<int:patient_id>", methods=["GET", "POST"])
def update_patient(patient_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]
        email = request.form["email"]

        cur.execute("""
            UPDATE patients
            SET name = %s, age = %s, gender = %s,
                phone = %s, address = %s, email = %s
            WHERE patient_id = %s
        """, (name, age, gender, phone, address, email, patient_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("view_patients"))
    

    cur.execute("""
        SELECT patient_id, name, age, gender, phone, address, email
        FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    patient = cur.fetchone()
    cur.close()
    conn.close()

    if patient is None:
        return "Patient not found", 404

    return render_template("update_patient.html", patient=patient)



@app.route("/delete_patient/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Delete treatments linked to the patient's appointments
        cur.execute("""
            DELETE FROM treatments
            WHERE appointment_id IN (
                SELECT appointment_id
                FROM appointments
                WHERE patient_id = %s
            )
        """, (patient_id,))

        # Delete appointments linked to the patient
        cur.execute(
            "DELETE FROM appointments WHERE patient_id = %s",
            (patient_id,)
        )

        # Delete bills linked to the patient
        cur.execute(
            "DELETE FROM bills WHERE patient_id = %s",
            (patient_id,)
        )

        # Delete the patient
        cur.execute(
            "DELETE FROM patients WHERE patient_id = %s",
            (patient_id,)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("view_patients"))


@app.route("/doctors")
def view_doctors():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM doctors
        ORDER BY doctor_id
    """)

    doctors = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("doctors.html", doctors=doctors)

@app.route("/appointments")
def view_appointments():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        a.appointment_id,
        p.name AS patient_name,
        d.name AS doctor_name,
        a.appointment_date
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    ORDER BY a.appointment_id
""")

    appointments = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("appointments.html", appointments=appointments)
@app.route("/appointment_report")

@app.route("/appointment_report")
def appointment_report():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.name AS doctor_name,
            p.name AS patient_name,
            a.appointment_date,
            
            COUNT(a.appointment_id) OVER (
                PARTITION BY d.doctor_id
            ) AS total_appointments
        FROM appointments a
        JOIN patients p
            ON a.patient_id = p.patient_id
        JOIN doctors d
            ON a.doctor_id = d.doctor_id
        ORDER BY d.name, a.appointment_date, a.appointment_time
    """)

    report = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("appointment_report.html", report=report)

@app.route("/billing_report")
def billing_report():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.name, SUM(b.amount) AS total_bill
        FROM patients p
        JOIN bills b ON p.patient_id = b.patient_id
        GROUP BY p.patient_id, p.name
        ORDER BY total_bill DESC
    """)

    report = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("billing_report.html", report=report)
@app.route("/doctor_report")
def doctor_report():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT d.name, COUNT(a.appointment_id) AS total_appointments
        FROM doctors d
        JOIN appointments a ON d.doctor_id = a.doctor_id
        GROUP BY d.doctor_id, d.name
        HAVING COUNT(a.appointment_id) > 1
        ORDER BY total_appointments DESC
    """)

    report = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("doctor_report.html", report=report)
@app.route("/high_bill_report")
def high_bill_report():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.name, b.amount
        FROM patients p
        JOIN bills b ON p.patient_id = b.patient_id
        WHERE b.amount > (
            SELECT AVG(amount)
            FROM bills
        )
        ORDER BY b.amount DESC
    """)

    report = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("high_bill_report.html", report=report)
@app.route("/payment_report")
def payment_report():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            payment_status,
            COUNT(*) AS total_bills,
            SUM(amount) AS total_amount
        FROM bills
        GROUP BY payment_status
        HAVING COUNT(*) > 0
        ORDER BY total_amount DESC
    """)

    report = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("payment_report.html", report=report)
@app.route("/treatments")
def view_treatments():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM treatments
        ORDER BY treatment_id
    """)

    treatments = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("treatments.html", treatments=treatments)
@app.route("/bills")
def view_bills():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.bill_id, p.name, b.amount, b.payment_status
        FROM bills b
        JOIN patients p ON b.patient_id = p.patient_id
        ORDER BY b.bill_id
    """)

    bills = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("bills.html", bills=bills)
if __name__ == "__main__":
    app.run(debug=True)
