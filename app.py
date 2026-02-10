from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_connection

app = Flask(__name__)

# 🔐 CLAVE SECRETA (obligatoria para sesiones y flash)
app.secret_key = "clave_super_secreta_123"

# -------------------------
# INDEX (PROTEGIDO)
# -------------------------
@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))

    q = request.args.get("q", "")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if q:
        cursor.execute("""
            SELECT id, nombre, curp, numero_control
            FROM certificados_01
            WHERE nombre LIKE %s OR numero_control LIKE %s
            ORDER BY nombre
        """, (f"%{q}%", f"%{q}%"))
    else:
        cursor.execute("""
            SELECT id, nombre, curp, numero_control
            FROM certificados_01
            ORDER BY nombre
        """)

    alumnos = cursor.fetchall()
    conn.close()

    return render_template("index.html", alumnos=alumnos)


# -------------------------
# REGISTRAR ALUMNO
# -------------------------
@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        curp = request.form["curp"]
        numero_control = request.form["numero_control"]

        if curp == "":
            curp = None

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO certificados_01 (nombre, curp, numero_control) VALUES (%s, %s, %s)",
                (nombre, curp, numero_control)
            )
            conn.commit()
            flash("Alumno registrado correctamente", "success")
        except Exception as e:
            flash("Error: número de control o CURP duplicado", "error")
            print(e)
        finally:
            conn.close()

        return redirect(url_for("index"))

    return render_template("registrar.html")


# -------------------------
# Editar alumno
# -------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        curp = request.form["curp"]
        numero_control = request.form["numero_control"]

        try:
            cursor.execute("""
                UPDATE certificados_01
                SET nombre=%s, curp=%s, numero_control=%s
                WHERE id=%s
            """, (nombre, curp, numero_control, id))
            conn.commit()
            flash("Alumno actualizado correctamente")
        except:
            flash("Error al actualizar (CURP o número duplicado)")
        finally:
            conn.close()

        return redirect(url_for("index"))

    cursor.execute("SELECT * FROM certificados_01 WHERE id=%s", (id,))
    alumno = cursor.fetchone()
    conn.close()

    return render_template("editar.html", alumno=alumno)


# -------------------------
# ELIMINAR ALUMNO
# -------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM certificados_01 WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    flash("Alumno eliminado correctamente")
    return redirect(url_for("index"))



# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        pwd = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario=%s AND password=%s",
            (user, pwd)
        )
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["usuario"] = user
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas", "error")

    return render_template("login.html")

# -------------------------
# LOGOUT (RECOMENDADO)
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
