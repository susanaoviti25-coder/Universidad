package org.example.vista;

import org.example.dao.AlumnoDAO;
import org.example.dao.ProfesorDAO;
import org.example.modelo.Alumno;
import org.example.modelo.Profesor;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

public class Menu {

    private static final BufferedReader entrada =
            new BufferedReader(new InputStreamReader(System.in));

    private static final AlumnoDAO alumnoDAO = new AlumnoDAO();
    private static final ProfesorDAO profesorDAO = new ProfesorDAO();

    //=========================================
    // REGISTRAR ALUMNO
    //=========================================

    public static void inscribir() throws IOException {

        Alumno alumno = new Alumno();

        System.out.println("\n========= REGISTRO DE ALUMNO =========");

        System.out.print("Número de expediente: ");
        alumno.setNumExpediente(Integer.parseInt(entrada.readLine()));

        System.out.print("Nombre completo: ");
        alumno.setNombre(entrada.readLine());

        System.out.print("Edad: ");
        alumno.setEdad(Integer.parseInt(entrada.readLine()));

        System.out.print("Carrera (TI, QUI, MEC, MKT): ");
        alumno.setCarrera(entrada.readLine());

        System.out.print("Cuatrimestre: ");
        alumno.setCuatrimestre(Integer.parseInt(entrada.readLine()));

        if (alumnoDAO.nuevoAlumno(alumno)) {
            System.out.println("\nAlumno registrado exitosamente.");
        } else {
            System.out.println("\nNo fue posible registrar al alumno.");
        }

    }

    //=========================================
    // MOSTRAR ALUMNOS
    //=========================================

    public static void mostrar() {

        ArrayList<Alumno> listaAlumnos = alumnoDAO.extraerAlumnos();

        System.out.println("\n========= LISTA DE ALUMNOS =========");

        if (listaAlumnos.isEmpty()) {

            System.out.println("No existen alumnos registrados.");

        } else {

            for (Alumno alumno : listaAlumnos) {

                System.out.println(alumno);

            }

        }

    }

    //=========================================
    // MODIFICAR ALUMNO
    //=========================================

    public static void modificar() throws IOException {

        Alumno alumno = new Alumno();

        System.out.println("\n========= MODIFICAR ALUMNO =========");

        System.out.print("Número de expediente: ");
        alumno.setNumExpediente(Integer.parseInt(entrada.readLine()));

        System.out.print("Nuevo nombre: ");
        alumno.setNombre(entrada.readLine());

        System.out.print("Nueva edad: ");
        alumno.setEdad(Integer.parseInt(entrada.readLine()));

        System.out.print("Nueva carrera (TI, QUI, MEC, MKT): ");
        alumno.setCarrera(entrada.readLine());

        System.out.print("Nuevo cuatrimestre: ");
        alumno.setCuatrimestre(Integer.parseInt(entrada.readLine()));

        alumnoDAO.actualizarAlumno(alumno);

    }
    //=========================================
    // BORRAR ALUMNO
    //=========================================

    public static void borrar() throws IOException {

        Alumno alumno = new Alumno();

        System.out.println("\n========= ELIMINAR ALUMNO =========");

        System.out.print("Número de expediente: ");
        alumno.setNumExpediente(Integer.parseInt(entrada.readLine()));

        if (alumnoDAO.borrarAlumno(alumno)) {
            System.out.println("Alumno eliminado correctamente.");
        } else {
            System.out.println("No fue posible eliminar el alumno.");
        }

    }

    //=========================================
    // BUSCAR ALUMNO
    //=========================================

    public static void buscar() throws IOException {

        Alumno alumno = new Alumno();

        System.out.println("\n========= BUSCAR ALUMNO =========");

        System.out.print("Número de expediente: ");
        alumno.setNumExpediente(Integer.parseInt(entrada.readLine()));

        boolean encontrado = alumnoDAO.buscarAlumno(alumno);

        if (encontrado) {

            System.out.println("\nAlumno encontrado:\n");
            System.out.println(alumno);

        } else {

            System.out.println("No existe un alumno con ese número de expediente.");

        }

    }

    //=========================================
    // REGISTRAR PROFESOR
    //=========================================

    public static void registrarProfesor() throws IOException {

        Profesor profesor = new Profesor();

        System.out.println("\n========= REGISTRO DE PROFESOR =========");

        System.out.print("Número de empleado: ");
        profesor.setNumEmpleado(Integer.parseInt(entrada.readLine()));

        System.out.print("Nombre: ");
        profesor.setNombre(entrada.readLine());

        System.out.print("Edad: ");
        profesor.setEdad(Integer.parseInt(entrada.readLine()));

        System.out.print("Puesto (GERENTE, DOCENTE, DIRECTOR): ");
        profesor.setPuesto(entrada.readLine());

        System.out.print("Cédula profesional: ");
        profesor.setCedulaProfesional(entrada.readLine());

        if (profesorDAO.nuevoProfesor(profesor)) {

            System.out.println("\nProfesor registrado correctamente.");

        } else {

            System.out.println("\nNo fue posible registrar al profesor.");

        }

    }

    //=========================================
    // MOSTRAR PROFESORES
    //=========================================

    public static void mostrarProfesores() {

        ArrayList<Profesor> listaProfesores = profesorDAO.extraerProfesor();

        System.out.println("\n========= LISTA DE PROFESORES =========");

        if (listaProfesores.isEmpty()) {

            System.out.println("No hay profesores registrados.");

        } else {

            for (Profesor profesor : listaProfesores) {

                System.out.println(profesor);

            }

        }

    }

    //=========================================
    // MODIFICAR PROFESOR
    //=========================================

    public static void modificarProfesor() throws IOException {

        Profesor profesor = new Profesor();

        System.out.println("\n========= MODIFICAR PROFESOR =========");

        System.out.print("Número de empleado: ");
        profesor.setNumEmpleado(Integer.parseInt(entrada.readLine()));

        System.out.print("Nuevo nombre: ");
        profesor.setNombre(entrada.readLine());

        System.out.print("Nueva edad: ");
        profesor.setEdad(Integer.parseInt(entrada.readLine()));

        System.out.print("Nuevo puesto (GERENTE, DOCENTE, DIRECTOR): ");
        profesor.setPuesto(entrada.readLine());

        System.out.print("Nueva cédula profesional: ");
        profesor.setCedulaProfesional(entrada.readLine());

        profesorDAO.updatePro(profesor);

    }
    //=========================================
    // BORRAR PROFESOR
    //=========================================

    public static void borrarProfesor() throws IOException {

        Profesor profesor = new Profesor();

        System.out.println("\n========= ELIMINAR PROFESOR =========");

        System.out.print("Número de empleado: ");
        profesor.setNumEmpleado(Integer.parseInt(entrada.readLine()));

        if (profesorDAO.deletePro(profesor)) {

            System.out.println("Profesor eliminado correctamente.");

        } else {

            System.out.println("No fue posible eliminar al profesor.");

        }

    }

    //=========================================
    // BUSCAR PROFESOR
    //=========================================

    public static void buscarProfesor() throws IOException {

        Profesor profesor = new Profesor();

        System.out.println("\n========= BUSCAR PROFESOR =========");

        System.out.print("Número de empleado: ");
        profesor.setNumEmpleado(Integer.parseInt(entrada.readLine()));

        ArrayList<Profesor> profesores = profesorDAO.buscarPro(profesor);

        if (profesores.isEmpty()) {

            System.out.println("No se encontró ningún profesor.");

        } else {

            System.out.println("\nProfesor(es) encontrado(s):\n");

            for (Profesor p : profesores) {

                System.out.println(p);

            }

        }

    }

    //=========================================
    // MENÚ PRINCIPAL
    //=========================================

    public static void menu() throws IOException {

        int opcion = 0;

        do {

            System.out.println("\n====================================");
            System.out.println("      SISTEMA UNIVERSIDAD");
            System.out.println("====================================");
            System.out.println("1. Registrar alumno");
            System.out.println("2. Mostrar alumnos");
            System.out.println("3. Modificar alumno");
            System.out.println("4. Eliminar alumno");
            System.out.println("5. Buscar alumno");
            System.out.println("6. Registrar profesor");
            System.out.println("7. Mostrar profesores");
            System.out.println("8. Modificar profesor");
            System.out.println("9. Eliminar profesor");
            System.out.println("10. Buscar profesor");
            System.out.println("11. Salir");
            System.out.print("Seleccione una opción: ");

            try {

                opcion = Integer.parseInt(entrada.readLine());

                switch (opcion) {

                    case 1:
                        inscribir();
                        break;

                    case 2:
                        mostrar();
                        break;

                    case 3:
                        modificar();
                        break;

                    case 4:
                        borrar();
                        break;

                    case 5:
                        buscar();
                        break;

                    case 6:
                        registrarProfesor();
                        break;

                    case 7:
                        mostrarProfesores();
                        break;

                    case 8:
                        modificarProfesor();
                        break;

                    case 9:
                        borrarProfesor();
                        break;

                    case 10:
                        buscarProfesor();
                        break;

                    case 11:
                        System.out.println("\nGracias por utilizar el sistema.");
                        break;

                    default:
                        System.out.println("La opción ingresada no es válida.");

                }

            } catch (NumberFormatException e) {

                System.out.println("Debes ingresar únicamente números.");

            }

        } while (opcion != 11);

    }

}