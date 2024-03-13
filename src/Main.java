import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Calculadora calculadora = new Calculadora(); // creamos una calculadora
        // iniciamos variables
        double num1 = 0;
        double num2 = 0;
        double resultado = 0;
        int opcion;
        do { // bucle hasta que la opcion sea=0
            System.out.println("CALCULADORA:");
            System.out.println("1.- Sumar");
            System.out.println("2.- Restar");
            System.out.println("3.- Multiplicar");
            System.out.println("4.- Dividir");
            System.out.println("0.- Salir");
            System.out.println("Introduce una opcion: ");
            opcion = scanner.nextInt();

            switch (opcion) {
                case 1:
                    // opción uno llama al metodo suma
                    // se pide al usuario dos números
                    System.out.println("Introduce el primer numero: ");
                    num1 = scanner.nextDouble();
                    System.out.println("Introduce el segundo numero: ");
                    num2 = scanner.nextDouble();
                    resultado = calculadora.sumar(num1, num2);
                    System.out.println("Resultado: " + resultado);// resultado
                    break;
                case 2:
                    // opción dos llama al metodo resta
                    // se pide al usuario dos números
                    System.out.println("Introduce el primer numero: ");
                    num1 = scanner.nextDouble();
                    System.out.println("Introduce el segundo numero: ");
                    num2 = scanner.nextDouble();
                    resultado = calculadora.restar(num1, num2);
                    System.out.println("Resultado: " + resultado);// resultado
                    break;
                case 3:
                    // opción tres llama al metodo multipliar
                    // se pide al usuario dos números
                    System.out.println("Introduce el primer numero: ");
                    num1 = scanner.nextDouble();
                    System.out.println("Introduce el segundo numero: ");
                    num2 = scanner.nextDouble();
                    resultado = calculadora.multiplicar(num1, num2);
                    System.out.println("Resultado: " + resultado);// resultado
                    break;
                case 4:
                    // opción cuatro llama al metodo dividir
                    // se pide al usuario dos números
                    System.out.println("Introduce el primer numero: ");
                    num1 = scanner.nextDouble();
                    System.out.println("Introduce el segundo numero: ");
                    num2 = scanner.nextDouble();
                    resultado = calculadora.dividir(num1, num2);
                    System.out.println("Resultado: " + resultado);// resultado
                    break;
                case 0:
                    // opción 0 cierra el programa
                    System.out.println("¡Adíos!");
                    break;
                default:
                    System.out.println("Opcion no valida. Intentalo de nuevo.");
            }
        } while (opcion != 0);

    }
}