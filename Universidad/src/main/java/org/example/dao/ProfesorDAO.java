package org.example.dao;

import org.example.config.Conexion;
import org.example.modelo.Profesor;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

public class ProfesorDAO {

    public ProfesorDAO() {
    }

    //=========================================
    // REGISTRAR PROFESOR
    //=========================================

    public boolean nuevoProfesor(Profesor profesor) {

        boolean registrado = false;

        String sql = "INSERT INTO profesores VALUES (?,?,?,?,?)";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(sql)
        ) {

            ps.setInt(1, profesor.getNumEmpleado());
            ps.setString(2, profesor.getNombre());
            ps.setInt(3, profesor.getEdad());
            ps.setString(4, profesor.getPuesto());
            ps.setString(5, profesor.getCedulaProfesional());

            int filas = ps.executeUpdate();

            if (filas > 0) {
                registrado = true;
                System.out.println("Profesor registrado correctamente.");
            }

        } catch (SQLException e) {

            System.out.println("No fue posible registrar al profesor.");
            System.out.println(e.getMessage());

        }

        return registrado;
    }

    //=========================================
    // MOSTRAR PROFESORES
    //=========================================

    public ArrayList<Profesor> extraerProfesor() {

        ArrayList<Profesor> listaProfesores = new ArrayList<>();

        String sql = "SELECT * FROM profesores";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(sql);
                ResultSet rs = ps.executeQuery()
        ) {

            while (rs.next()) {

                Profesor profesor = new Profesor();

                profesor.setNumEmpleado(rs.getInt("numEmpleado"));
                profesor.setNombre(rs.getString("nombre"));
                profesor.setEdad(rs.getInt("edad"));
                profesor.setPuesto(rs.getString("puesto"));
                profesor.setCedulaProfesional(rs.getString("cedulaProfesional"));

                listaProfesores.add(profesor);

            }

        } catch (SQLException e) {

            System.out.println("Error al consultar los profesores.");
            System.out.println(e.getMessage());

        }

        return listaProfesores;
    }
    //=========================================
    // ACTUALIZAR PROFESOR
    //=========================================

    public boolean updatePro(Profesor profesor) {

        boolean actualizado = false;

        String sql = "UPDATE profesores SET nombre = ?, edad = ?, puesto = ?, cedulaProfesional = ? WHERE numEmpleado = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(sql)
        ) {

            ps.setString(1, profesor.getNombre());
            ps.setInt(2, profesor.getEdad());
            ps.setString(3, profesor.getPuesto());
            ps.setString(4, profesor.getCedulaProfesional());
            ps.setInt(5, profesor.getNumEmpleado());

            int filas = ps.executeUpdate();

            if (filas > 0) {

                actualizado = true;
                System.out.println("Profesor actualizado correctamente.");

            } else {

                System.out.println("No existe un profesor con ese número de empleado.");

            }

        } catch (SQLException e) {

            System.out.println("Ocurrió un error al actualizar el profesor.");
            System.out.println(e.getMessage());

        }

        return actualizado;
    }

    //=========================================
    // ELIMINAR PROFESOR
    //=========================================

    public boolean deletePro(Profesor profesor) {

        boolean eliminado = false;

        String sql = "DELETE FROM profesores WHERE numEmpleado = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(sql)
        ) {

            ps.setInt(1, profesor.getNumEmpleado());

            int filas = ps.executeUpdate();

            if (filas > 0) {

                eliminado = true;
                System.out.println("Profesor eliminado correctamente.");

            } else {

                System.out.println("No se encontró el profesor para eliminar.");

            }

        } catch (SQLException e) {

            System.out.println("Error al eliminar el profesor.");
            System.out.println(e.getMessage());

        }

        return eliminado;
    }

    //=========================================
    // BUSCAR PROFESOR
    //=========================================

    public ArrayList<Profesor> buscarPro(Profesor profesor) {

        ArrayList<Profesor> resultado = new ArrayList<>();

        String sql = "SELECT * FROM profesores WHERE numEmpleado = ?";

        try (
                Connection conn = Conexion.conectar();
                PreparedStatement ps = conn.prepareStatement(sql)
        ) {

            ps.setInt(1, profesor.getNumEmpleado());

            try (ResultSet rs = ps.executeQuery()) {

                while (rs.next()) {

                    Profesor encontrado = new Profesor();

                    encontrado.setNumEmpleado(rs.getInt("numEmpleado"));
                    encontrado.setNombre(rs.getString("nombre"));
                    encontrado.setEdad(rs.getInt("edad"));
                    encontrado.setPuesto(rs.getString("puesto"));
                    encontrado.setCedulaProfesional(rs.getString("cedulaProfesional"));

                    resultado.add(encontrado);

                }

            }

        } catch (SQLException e) {

            System.out.println("Error durante la búsqueda del profesor.");
            System.out.println(e.getMessage());

        }

        return resultado;
    }

}