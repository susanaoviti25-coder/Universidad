package org.example.modelo;

import java.util.Locale;

public class Profesor {

    private int numEmpleado;
    private String nombre;
    private int edad;
    private String puesto;
    private String cedulaProfesional;

    // Puestos permitidos
    private final String[] puestosDisponibles = {
            "GERENTE",
            "DOCENTE",
            "DIRECTOR"
    };

    public Profesor() {
    }

    public Profesor(int numEmpleado, String nombre, int edad,
                    String puesto, String cedulaProfesional) {

        this.numEmpleado = numEmpleado;
        setNombre(nombre);
        setEdad(edad);
        setPuesto(puesto);
        setCedulaProfesional(cedulaProfesional);
    }

    //=========================
    // GETTERS
    //=========================

    public int getNumEmpleado() {
        return numEmpleado;
    }

    public String getNombre() {
        return nombre.toUpperCase(Locale.ROOT);
    }

    public int getEdad() {
        return edad;
    }

    public String getPuesto() {
        return puesto;
    }

    public String getCedulaProfesional() {
        return cedulaProfesional;
    }

    //=========================
    // SETTERS
    //=========================

    public void setNumEmpleado(int numEmpleado) {
        this.numEmpleado = numEmpleado;
    }

    public void setNombre(String nombre) {

        if (nombre != null && !nombre.trim().isEmpty()) {
            this.nombre = nombre.trim();
        } else {
            System.out.println("Debe ingresar un nombre válido.");
        }

    }

    public void setEdad(int edad) {

        if (edad >= 18 && edad <= 109) {
            this.edad = edad;
        } else {
            System.out.println("La edad permitida es de 18 a 109 años.");
        }

    }

    public void setPuesto(String puesto) {

        if (esPuestoValido(puesto)) {
            this.puesto = puesto.toUpperCase();
        } else {
            System.out.println("El puesto indicado no es válido.");
        }

    }

    public void setCedulaProfesional(String cedulaProfesional) {

        if (cedulaProfesional != null && !cedulaProfesional.trim().isEmpty()) {
            this.cedulaProfesional = cedulaProfesional.trim();
        } else {
            System.out.println("Debe capturar una cédula profesional.");
        }

    }

    //=========================
    // VALIDACIÓN
    //=========================

    private boolean esPuestoValido(String puesto) {

        for (String p : puestosDisponibles) {

            if (p.equalsIgnoreCase(puesto)) {
                return true;
            }

        }

        return false;
    }

    //=========================
    // TOSTRING
    //=========================

    @Override
    public String toString() {

        StringBuilder informacion = new StringBuilder();

        informacion.append("---------------------------------\n");
        informacion.append("Empleado : ").append(numEmpleado).append("\n");
        informacion.append("Nombre   : ").append(nombre).append("\n");
        informacion.append("Edad     : ").append(edad).append("\n");
        informacion.append("Puesto   : ").append(puesto).append("\n");
        informacion.append("Cédula   : ").append(cedulaProfesional).append("\n");
        informacion.append("---------------------------------");

        return informacion.toString();
    }

}