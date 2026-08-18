package org.example;

import org.example.vista.Menu;

public class Main {

    public static void main(String[] args) {

        try {

            Menu.menu();

        } catch (Exception e) {

            System.out.println("Se produjo un error al iniciar el sistema.");
            System.out.println("Detalle: " + e.getMessage());

        }

    }

}