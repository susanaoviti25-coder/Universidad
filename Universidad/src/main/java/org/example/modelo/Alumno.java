package org.example.modelo;

import java.util.Locale;

public class Alumno {

    private int numExpediente;
    private String nombre;
    private int edad;
    private String carrera;
    private int cuatrimestre;

    // Carreras permitidas
    private final String[] carrerasDisponibles = {
            "TI",
            "QUI",
            "MEC",
            "MKT"
    };

    public Alumno() {
    }

    public Alumno(int numExpediente, String nombre, int edad, String carrera, int cuatrimestre) {

        this.numExpediente = numExpediente;
        setNombre(nombre);
        setEdad(edad);
        setCarrera(carrera);
        setCuatrimestre(cuatrimestre);

    }

    //======================
    // GETTERS
    //======================

    public int getNumExpediente() {
        return numExpediente;
    }

    public String getNombre() {
        return nombre.toUpperCase(Locale.ROOT);
    }

    public int getEdad() {
        return edad;
    }

    public String getCarrera() {
        return carrera;
    }

    public int getCuatrimestre() {
        return cuatrimestre;
    }

    //======================
    // SETTERS
    //======================

    public void setNumExpediente(int numExpediente) {
        this.numExpediente = numExpediente;
    }

    public void setNombre(String nombre) {

        if (nombre != null && !nombre.trim().isEmpty()) {
            this.nombre = nombre.trim();
        } else {
            System.out.println("Debe escribir un nombre válido.");
        }

    }

    public void setEdad(int edad) {

        if (edad >= 16 && edad <= 109) {
            this.edad = edad;
        } else {
            System.out.println("Edad fuera del rango permitido.");
        }

    }

    public void setCarrera(String carrera) {

        if (esCarreraValida(carrera)) {
            this.carrera = carrera.toUpperCase();
        } else {
            System.out.println("La carrera ingresada no existe.");
        }

    }

    public void setCuatrimestre(int cuatrimestre) {

        if (cuatrimestre >= 1 && cuatrimestre <= 11) {
            this.cuatrimestre = cuatrimestre;
        } else {
            System.out.println("El cuatrimestre debe estar entre 1 y 11.");
        }

    }

    //======================
    // VALIDACIONES
    //======================

    private boolean esCarreraValida(String carrera) {

        for (String c : carrerasDisponibles) {

            if (c.equalsIgnoreCase(carrera)) {
                return true;
            }

        }

        return false;
    }

    //======================
    // MÉTODO TOSTRING
    //======================

    @Override
    public String toString() {

        StringBuilder datos = new StringBuilder();

        datos.append("---------------------------------\n");
        datos.append("Expediente : ").append(numExpediente).append("\n");
        datos.append("Nombre     : ").append(nombre).append("\n");
        datos.append("Edad       : ").append(edad).append("\n");
        datos.append("Carrera    : ").append(carrera).append("\n");
        datos.append("Cuatrimestre: ").append(cuatrimestre).append("\n");
        datos.append("---------------------------------");

        return datos.toString();

    }

}