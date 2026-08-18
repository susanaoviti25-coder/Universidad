package org.example.dao;

import org.example.config.Conexion;
import org.example.modelo.Alumno;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

public class AlumnoDAO {

    public AlumnoDAO() {
    }

    //=========================================
    // REGISTRAR ALUMNO
    //=========================================

    public boolean nuevoAlumno(Alumno alumno) {

        boolean guardado = false;

        String consulta = "INSERT INTO alumnos VALUES (?,?,?,?,?)";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(consulta)
        ) {

            ps.setInt(1, alumno.getNumExpediente());
            ps.setString(2, alumno.getNombre());
            ps.setInt(3, alumno.getEdad());
            ps.setString(4, alumno.getCarrera());
            ps.setInt(5, alumno.getCuatrimestre());

            int filas = ps.executeUpdate();

            if (filas > 0) {
                guardado = true;
                System.out.println("Alumno registrado correctamente.");
            }

        } catch (SQLException e) {

            System.out.println("Ocurrió un problema al guardar el alumno.");
            System.out.println(e.getMessage());

        }

        return guardado;
    }

    //=========================================
    // MOSTRAR TODOS LOS ALUMNOS
    //=========================================

    public ArrayList<Alumno> extraerAlumnos() {

        ArrayList<Alumno> lista = new ArrayList<>();

        String consulta = "SELECT * FROM alumnos";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(consulta);
                ResultSet rs = ps.executeQuery()
        ) {

            while (rs.next()) {

                Alumno alumno = new Alumno();

                alumno.setNumExpediente(rs.getInt("numExpediente"));
                alumno.setNombre(rs.getString("nombre"));
                alumno.setEdad(rs.getInt("edad"));
                alumno.setCarrera(rs.getString("carrera"));
                alumno.setCuatrimestre(rs.getInt("cuatrimestre"));

                lista.add(alumno);
            }

        } catch (SQLException e) {

            System.out.println("Error al recuperar los alumnos.");
            System.out.println(e.getMessage());

        }

        return lista;
    }

    //=========================================
    // ACTUALIZAR ALUMNO
    //=========================================

    public boolean actualizarAlumno(Alumno alumno) {

        boolean actualizado = false;

        String consulta = "UPDATE alumnos SET nombre = ?, edad = ?, carrera = ?, cuatrimestre = ? WHERE numExpediente = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(consulta)
        ) {

            ps.setString(1, alumno.getNombre());
            ps.setInt(2, alumno.getEdad());
            ps.setString(3, alumno.getCarrera());
            ps.setInt(4, alumno.getCuatrimestre());
            ps.setInt(5, alumno.getNumExpediente());

            if (ps.executeUpdate() > 0) {

                actualizado = true;
                System.out.println("Información del alumno actualizada.");

            } else {

                System.out.println("No existe un alumno con ese número de expediente.");

            }

        } catch (SQLException e) {

            System.out.println("No fue posible actualizar el registro.");
            System.out.println(e.getMessage());

        }

        return actualizado;
    }

    //=========================================
    // ELIMINAR ALUMNO
    //=========================================

    public boolean borrarAlumno(Alumno alumno) {

        boolean eliminado = false;

        String consulta = "DELETE FROM alumnos WHERE numExpediente = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(consulta)
        ) {

            ps.setInt(1, alumno.getNumExpediente());

            int filas = ps.executeUpdate();

            if (filas > 0) {

                eliminado = true;
                System.out.println("Alumno eliminado correctamente.");

            } else {

                System.out.println("No fue posible eliminar el alumno.");

            }

        } catch (SQLException e) {

            System.out.println("Error al eliminar el alumno.");
            System.out.println(e.getMessage());

        }

        return eliminado;
    }

    //=========================================
    // BUSCAR ALUMNO
    //=========================================

    public boolean buscarAlumno(Alumno alumno) {

        boolean encontrado = false;

        String consulta = "SELECT * FROM alumnos WHERE numExpediente = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(consulta)
        ) {

            ps.setInt(1, alumno.getNumExpediente());

            try (ResultSet rs = ps.executeQuery()) {

                if (rs.next()) {

                    alumno.setNombre(rs.getString("nombre"));
                    alumno.setEdad(rs.getInt("edad"));
                    alumno.setCarrera(rs.getString("carrera"));
                    alumno.setCuatrimestre(rs.getInt("cuatrimestre"));

                    encontrado = true;

                }

            }

        } catch (SQLException e) {

            System.out.println("Error durante la búsqueda.");
            System.out.println(e.getMessage());

        }

        return encontrado;
    }

}