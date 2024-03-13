public class Calculadora {
    /**
     * Método dividir
     * @param a El primer número a sumar.
     * @param b El segundo número a sumar.
     * @return La division de los dos números.
     */
    public double dividir(double a, double b) {
        if (b == 0) {//si el segundo número es 0 devuelve 0
            return 0;
        }
        return (a / b);
    }


}
