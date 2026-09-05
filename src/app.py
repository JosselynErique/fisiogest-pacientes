from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        cedula = request.form["cedula"]
        nombres = request.form["nombres"]
        apellidos = request.form["apellidos"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        correo = request.form["correo"]

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