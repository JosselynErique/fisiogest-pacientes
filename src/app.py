from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        cedula = request.form.get("cedula", "").strip()
        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        correo = request.form.get("correo", "").strip()

        if not cedula or not nombres or not apellidos:
            return "Los campos cédula, nombres y apellidos son obligatorios.", 400

        print("Paciente registrado:")
        print("Cédula:", cedula)
        print("Nombres:", nombres)
        print("Apellidos:", apellidos)
        print("Teléfono:", telefono)
        print("Dirección:", direccion)
        print("Correo:", correo)

        return "Paciente registrado correctamente"

    return render_template("registrar.html")


if __name__ == "__main__":
    app.run(debug=True)