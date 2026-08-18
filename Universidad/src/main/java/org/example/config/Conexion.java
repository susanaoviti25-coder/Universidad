package org.example.config;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Conexion {

    // Datos de la base de datos
    private static final String URL = "jdbc:mysql://localhost:3306/Universidad";
    private static final String USUARIO = "root";
    private static final String PASSWORD = "2025162034";

    // Constructor privado para evitar instancias
    private Conexion() {
    }

    /**
     * Establece la conexión con la base de datos.
     * @return Connection
     */
    public static Connection conectar() {

        Connection conn = null;

        try {

            conn = DriverManager.getConnection(URL, USUARIO, PASSWORD);
            System.out.println("Conexión establecida correctamente.");

        } catch (SQLException e) {

            System.out.println("No fue posible conectarse a la base de datos.");
            System.out.println("Detalle del error: " + e.getMessage());

        }

        return conn;
    }

}